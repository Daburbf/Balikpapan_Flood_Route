from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QMessageBox, QSplitter, 
                             QLineEdit, QListWidget, QListWidgetItem, 
                             QRadioButton, QGroupBox, QFormLayout, QApplication)
from PyQt5.QtCore import Qt, QTimer
import os
import json
from math import radians, cos, sin, asin, sqrt

# Import Core System
from core.place_loader import load_places_from_csv
from ui.map_widget import MapWidget
from core.graph import Graph
from core.dijkstra import Dijkstra

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. INISIALISASI PETA (Hanya sekali di awal)
        print("⏳ Sedang memuat data peta...")
        self.graph = Graph() 
        
        # --- PERBAIKAN FREEZE ---
        # Kita simpan cadangan graph yang masih bersih di RAM
        # Agar saat reset tidak perlu baca file lagi dari awal.
        self.graph_backup = self.graph.G.copy() 
        print("✅ Backup peta disimpan di memori.")
        
        self.dijkstra = Dijkstra(self.graph)
        
        self.flood_data = []      # Data banjir JSON (Lingkaran)
        self.flood_polygons = []  # Data banjir User (Bentuk Bebas)
        self.temp_flood_points = [] # Titik sementara saat menggambar
        
        self.search_data = [] 
        self.start_location = None
        self.end_location = None
        
        self.click_mode = "start" 

        # 2. Load Data Tambahan
        self.init_data()
        self.extract_streets_from_osm() 
        
        # 3. Setup Tampilan
        self.init_ui()
        
        # 4. Hubungkan Signal Klik Peta
        try:
            self.map_widget.map_clicked_signal.connect(self.handle_map_click)
        except AttributeError:
            print("Warning: MapWidget belum support klik.")

    def init_data(self):
        # Reset data banjir
        self.flood_data = []

        # --- 1. LOAD DATA BANJIR (DARI FOLDER DATA) ---
        # Kita gunakan os.path.join agar aman di Windows/Mac
        target_file = os.path.join('data', 'locations_balikpapan.json')
        
        # Cek apakah file ada
        if os.path.exists(target_file):
            try:
                with open(target_file, 'r') as f:
                    data = json.load(f)
                    raw_points = data.get('locations', [])
                    
                    valid_count = 0
                    for p in raw_points:
                        # Filter Null
                        if p.get('latitude') is not None and p.get('longitude') is not None:
                            clean_point = {
                                'latitude': float(p['latitude']),
                                'longitude': float(p['longitude']),
                                'radius': 150, 
                                'description': p.get('name', 'Area Banjir')
                            }
                            self.flood_data.append(clean_point)
                            valid_count += 1
                            
                    print(f"✅ Data Banjir: {valid_count} titik dimuat dari 'data/locations_balikpapan.json'.")
                    
            except Exception as e:
                print(f"❌ Gagal membaca JSON: {e}")
        else:
            print(f"⚠️ File tidak ditemukan: {target_file}")

        # --- TERAPKAN KE GRAPH ---
        if self.flood_data:
            self.graph.apply_flood_data(self.flood_data)
            if hasattr(self, 'graph_backup'):
                self.apply_flood_to_graph_obj(self.graph_backup, self.flood_data)
        else:
            print("ℹ️ Tidak ada data banjir aktif.")

        # --- 2. LOAD DATA LOKASI UMUM (HARDCODED) ---
        self.search_data = [
            {'name': 'Bandara SAMS Sepinggan', 'lat': -1.268, 'lon': 116.894},
            {'name': 'Plaza Balikpapan', 'lat': -1.262, 'lon': 116.832},
            {'name': 'Pelabuhan Semayang', 'lat': -1.279, 'lon': 116.807},
            {'name': 'Lapangan Merdeka', 'lat': -1.275, 'lon': 116.820},
        ]

        # --- 3. LOAD DATA TEMPAT (DARI FOLDER DATA) ---
        print("📂 Membaca CSV dari folder data...")
        csv_path = os.path.join('data', 'tempat_balikpapan.csv')
        
        try:
            # Kita panggil loader dengan path lengkap 'data/tempat_balikpapan.csv'
            csv_places = load_places_from_csv(csv_path)
            
            count_csv = 0
            for name, coords in csv_places.items():
                self.search_data.append({
                    'name': name, 'lat': coords[0], 'lon': coords[1]    
                })
                count_csv += 1
            print(f"✅ CSV Loaded: {count_csv} tempat berhasil ditambahkan.")
            
        except Exception as e:
            print(f"❌ Gagal memuat CSV: {e}")
        
    def apply_flood_to_graph_obj(self, G_obj, flood_points):
        """Helper function untuk menerapkan flood ke object graph tertentu (bukan self.graph)"""
        # Kita duplikasi logika apply_flood_data di sini untuk objek backup
        # Asumsi: radius banjir sederhana
        nodes_to_remove = []
        for node, data in G_obj.nodes(data=True):
            n_lat, n_lon = data['y'], data['x']
            for flood in flood_points:
                dist = sqrt((n_lat - flood['latitude'])**2 + (n_lon - flood['longitude'])**2)
                # Konversi kasar derajat ke meter (di ekuator 1 derajat ~ 111km)
                dist_meter = dist * 111000
                if dist_meter <= flood.get('radius', 100):
                    nodes_to_remove.append(node)
                    break
        for node in nodes_to_remove:
            if G_obj.has_node(node):
                G_obj.remove_node(node)

    def extract_streets_from_osm(self):
        print("Mengindeks nama jalan...")
        try:
            G = self.graph.G
            seen_names = set()
            for u, v, data in G.edges(data=True):
                if 'name' in data:
                    name = data['name']
                    if isinstance(name, list): name = name[0]
                    if name and name not in seen_names:
                        seen_names.add(name)
                        node_data = G.nodes[u]
                        self.search_data.append({
                            'name': str(name),
                            'lat': node_data['y'], 'lon': node_data['x']
                        })
        except Exception:
            pass

    def init_ui(self):
        self.setWindowTitle("BALIKPAPAN FLOOD SAFE ROUTE")
        self.setGeometry(100, 50, 1400, 900)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; } QLabel { color: white; }")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 1000])
        main_layout.addWidget(splitter)
        
        QTimer.singleShot(1000, self.initialize_map)
        
    def initialize_map(self):
        self.map_widget.load_map()
        # Gambar ulang semua banjir (Json + User Polygon)
        if self.flood_data:
            self.map_widget.add_flood_areas(self.flood_data)
        
        for poly in self.flood_polygons:
             self.map_widget.add_flood_polygon(poly)
             
        self.map_widget.set_status(f"Siap.")

    # --- LOGIKA KLIK PETA ---
    def set_mode(self, mode):
        self.click_mode = mode
        # Reset temp points jika ganti mode
        self.temp_flood_points = []
        
        if mode == "flood":
            self.btn_finish_flood.show()
            self.flood_warning.setText("Mode: Klik peta beberapa kali untuk area banjir.")
        else:
            self.btn_finish_flood.hide()
            self.flood_warning.setText("Status: Menunggu")

    def handle_map_click(self, lat, lon):
        print(f"Klik: {lat}, {lon} (Mode: {self.click_mode})")
        
        if self.click_mode == "start":
            self.start_location = {'name': f"Peta ({lat:.4f}, {lon:.4f})", 'lat': lat, 'lon': lon}
            self.start_input.setText(self.start_location['name'])
            self.map_widget.add_start_marker([lat, lon], "START")
            
        elif self.click_mode == "end":
            self.end_location = {'name': f"Peta ({lat:.4f}, {lon:.4f})", 'lat': lat, 'lon': lon}
            self.dest_input.setText(self.end_location['name'])
            self.map_widget.add_end_marker([lat, lon], "FINISH")
            
        elif self.click_mode == "flood":
            self.temp_flood_points.append([lat, lon])
            self.map_widget.add_temp_marker_visual(lat, lon)
            count = len(self.temp_flood_points)
            self.flood_warning.setText(f"Titik banjir terkumpul: {count} (Klik Selesai untuk proses)")

    def finish_flood_drawing(self):
        if len(self.temp_flood_points) < 3:
            QMessageBox.warning(self, "Kurang Titik", "Minimal butuh 3 titik untuk membuat area.")
            return

        # 1. Simpan Polygon
        poly_points = list(self.temp_flood_points) # Copy
        self.flood_polygons.append(poly_points)
        
        # 2. Update Graph (Blokir node di dalam polygon)
        # Gunakan QApplication.processEvents() agar UI tidak macet saat menghitung
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.map_widget.set_status("Sedang memproses area banjir...")
        QApplication.processEvents()
        
        blocked_count = self.apply_polygon_flood_to_graph(poly_points)
        
        QApplication.restoreOverrideCursor()
        
        # 3. Gambar Polygon Merah di Peta
        self.map_widget.add_flood_polygon(poly_points)
        
        # 4. Reset
        self.temp_flood_points = []
        self.flood_warning.setText(f"Area Banjir dibuat! {blocked_count} titik jalan diblokir.")
        QMessageBox.information(self, "Banjir Terbentuk", f"Area banjir berhasil dibuat.\n{blocked_count} titik jalan telah ditutup.")

    def apply_polygon_flood_to_graph(self, polygon_coords):
        """Mencari node graph yang ada di dalam polygon dan menghapusnya"""
        G = self.graph.G
        nodes_to_remove = []
        
        def is_inside(lat, lon, poly):
            inside = False
            j = len(poly) - 1
            for i in range(len(poly)):
                xi, yi = poly[i] # lat, lon
                xj, yj = poly[j]
                intersect = ((yi > lon) != (yj > lon)) and \
                    (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi)
                if intersect:
                    inside = not inside
                j = i
            return inside

        for node, data in G.nodes(data=True):
            n_lat = data['y']
            n_lon = data['x']
            
            if is_inside(n_lat, n_lon, polygon_coords):
                nodes_to_remove.append(node)
                
        for node in nodes_to_remove:
            if G.has_node(node):
                G.remove_node(node)
                
        return len(nodes_to_remove)

    def find_route(self):
        if not self.start_location or not self.end_location:
            QMessageBox.warning(self, "Input Kurang", "Pilih Lokasi Awal dan Tujuan dulu.")
            return

        self.map_widget.set_status("Menghitung rute...")
        QApplication.setOverrideCursor(Qt.WaitCursor) # Ubah kursor jadi loading
        QApplication.processEvents() # Refresh UI
        
        try:
            route_coords = self.dijkstra.find_route(
                self.start_location['lat'], self.start_location['lon'],
                self.end_location['lat'], self.end_location['lon']
            )
            
            if route_coords:
                self.map_widget.clear_routes() 
                self.update_map_markers() 
                self.map_widget.draw_route(route_coords, color='#3b82f6')
                
                total_km = self.calculate_distance(route_coords)
                
                time_car = (total_km / 30) * 60 
                time_bike = (total_km / 40) * 60
                time_walk = (total_km / 4) * 60
                
                self.lbl_dist.setText(f"{total_km:.2f} km")
                self.lbl_time_car.setText(f"{int(time_car)} menit")
                self.lbl_time_bike.setText(f"{int(time_bike)} menit")
                self.lbl_time_walk.setText(f"{int(time_walk)} menit")
                
                self.map_widget.set_status("Rute Aman Ditemukan!")
                self.flood_warning.setText("Rute Aman Ditemukan")
                self.flood_warning.setStyleSheet("color: #10b981; font-weight: bold;")
            else:
                QMessageBox.information(self, "Gagal", "Tidak ada jalur aman. Lokasi mungkin terkepung banjir.")
        except Exception as e:
            print(f"Error Routing: {e}")
        finally:
            QApplication.restoreOverrideCursor() # Kembalikan kursor

    def calculate_distance(self, coords):
        total_dist = 0
        R = 6371 
        for i in range(len(coords)-1):
            lat1, lon1 = coords[i]
            lat2, lon2 = coords[i+1]
            dLat = radians(lat2 - lat1)
            dLon = radians(lon2 - lon1)
            a = sin(dLat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2)**2
            c = 2 * asin(sqrt(a))
            total_dist += R * c
        return total_dist

    def reset_app(self):
        """Mereset aplikasi ke kondisi awal bersih (TANPA FREEZE)"""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.map_widget.set_status("Mereset sistem...")
        QApplication.processEvents()

        # 1. Reset UI
        self.start_input.clear()
        self.dest_input.clear()
        self.start_location = None
        self.end_location = None
        
        self.lbl_dist.setText("- km")
        self.lbl_time_car.setText("- menit")
        self.lbl_time_bike.setText("- menit")
        self.lbl_time_walk.setText("- menit")
        
        self.flood_warning.setText("Status: Menunggu")
        self.flood_warning.setStyleSheet("color: white;")
        
        # 2. Reset Data User
        self.flood_polygons = []
        self.temp_flood_points = []
        
        # 3. RESET GRAPH (Penyebab Freeze sebelumnya)
        # JANGAN lakukan: self.graph = Graph()
        # LAKUKAN ini: Restore dari backup memori
        print("Mereset graph dari backup memori...")
        self.graph.G = self.graph_backup.copy() 
        
        # Re-initialize Dijkstra dengan graph yang baru di-restore
        self.dijkstra = Dijkstra(self.graph)
        
        print("Graph berhasil direset.")

        self.rb_start.setChecked(True)
        self.set_mode("start")

        self.initialize_map()
        self.map_widget.set_status("Peta berhasil direset.")
        QApplication.restoreOverrideCursor()

    # --- UI COMPONENTS ---
    def create_left_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #1e293b; color: white;")
        layout = QVBoxLayout(panel)
        
        layout.addWidget(QLabel("<h2>BALIKPAPAN NAV</h2>"))
        
        # --- PANEL KONTROL KLIK ---
        mode_group = QGroupBox("Mode Klik Peta")
        mode_group.setStyleSheet("QGroupBox { border: 1px solid #94a3b8; margin-top: 5px; padding: 10px; border-radius: 5px; }")
        mode_layout = QVBoxLayout()
        
        self.rb_start = QRadioButton("Set Lokasi Awal")
        self.rb_end = QRadioButton("Set Tujuan")
        self.rb_flood = QRadioButton("Gambar Area Banjir") 
        
        rb_style = "QRadioButton { color: white; padding: 5px; } QRadioButton::indicator { width: 15px; height: 15px; }"
        self.rb_start.setStyleSheet(rb_style)
        self.rb_end.setStyleSheet(rb_style)
        self.rb_flood.setStyleSheet(rb_style)
        
        self.rb_start.setChecked(True)
        self.rb_start.toggled.connect(lambda: self.set_mode("start"))
        self.rb_end.toggled.connect(lambda: self.set_mode("end"))
        self.rb_flood.toggled.connect(lambda: self.set_mode("flood"))
        
        mode_layout.addWidget(self.rb_start)
        mode_layout.addWidget(self.rb_end)
        mode_layout.addWidget(self.rb_flood)
        
        # Tombol khusus Selesai Gambar
        self.btn_finish_flood = QPushButton("SELESAI GAMBAR")
        self.btn_finish_flood.setStyleSheet("background-color: #eab308; color: black; font-weight: bold; padding: 5px;")
        self.btn_finish_flood.clicked.connect(self.finish_flood_drawing)
        self.btn_finish_flood.hide()
        mode_layout.addWidget(self.btn_finish_flood)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        layout.addSpacing(10)

        # INPUT TEXT
        layout.addWidget(QLabel("Lokasi Awal:"))
        self.start_input = QLineEdit()
        self.start_input.setStyleSheet("padding: 8px; color: black; border-radius: 4px; background: #f1f5f9;")
        layout.addWidget(self.start_input)
        
        self.start_suggestions = QListWidget()
        self.start_suggestions.hide()
        self.start_suggestions.setStyleSheet("color: black; background: white;")
        self.start_suggestions.itemClicked.connect(self.on_start_selected)
        layout.addWidget(self.start_suggestions)

        layout.addWidget(QLabel("Tujuan:"))
        self.dest_input = QLineEdit()
        self.dest_input.setStyleSheet("padding: 8px; color: black; border-radius: 4px; background: #f1f5f9;")
        layout.addWidget(self.dest_input)
        
        self.dest_suggestions = QListWidget()
        self.dest_suggestions.hide()
        self.dest_suggestions.setStyleSheet("color: black; background: white;")
        self.dest_suggestions.itemClicked.connect(self.on_dest_selected)
        layout.addWidget(self.dest_suggestions)

        layout.addSpacing(15)

        # TOMBOL ACTION
        self.btn_route = QPushButton("CARI RUTE AMAN")
        self.btn_route.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; padding: 12px; font-weight: bold;
                border-radius: 6px; color: white;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_route.clicked.connect(self.find_route)
        layout.addWidget(self.btn_route)
        
        self.btn_reset = QPushButton("RESET SEMUA")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #dc2626; padding: 10px; font-weight: bold;
                border-radius: 6px; color: white; margin-top: 5px;
            }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        self.btn_reset.clicked.connect(self.reset_app)
        layout.addWidget(self.btn_reset)
        
        # --- INFO ---
        info_group = QGroupBox("Estimasi Perjalanan")
        info_group.setStyleSheet("QGroupBox { border: 1px solid #3b82f6; margin-top: 15px; padding: 10px; border-radius: 5px; color: white; }")
        info_layout = QFormLayout()
        
        self.lbl_dist = QLabel("- km")
        self.lbl_time_car = QLabel("- menit")
        self.lbl_time_bike = QLabel("- menit")
        self.lbl_time_walk = QLabel("- menit")
        
        val_style = "font-weight: bold; color: #fbbf24;"
        self.lbl_dist.setStyleSheet(val_style)
        self.lbl_time_car.setStyleSheet(val_style)
        self.lbl_time_bike.setStyleSheet(val_style)
        self.lbl_time_walk.setStyleSheet(val_style)
        
        info_layout.addRow("Jarak Total:", self.lbl_dist)
        info_layout.addRow("Mobil:", self.lbl_time_car)
        info_layout.addRow("Motor:", self.lbl_time_bike)
        info_layout.addRow("Jalan Kaki:", self.lbl_time_walk)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addSpacing(10)
        self.flood_warning = QLabel("Status: Menunggu")
        self.flood_warning.setWordWrap(True)
        layout.addWidget(self.flood_warning)
        layout.addStretch()
        
        self.start_input.textChanged.connect(lambda t: self.filter_suggestions(t, self.start_suggestions))
        self.dest_input.textChanged.connect(lambda t: self.filter_suggestions(t, self.dest_suggestions))
        
        return panel

    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0,0,0,0)
        self.map_widget = MapWidget()
        layout.addWidget(self.map_widget)
        return panel

    def filter_suggestions(self, text, list_widget):
        if len(text) < 3: 
            list_widget.hide()
            return
        text = text.lower()
        matches = []
        for item in self.search_data:
            if text in item['name'].lower():
                matches.append(item)
                if len(matches) > 20: break 
        list_widget.clear()
        if matches:
            for loc in matches:
                item = QListWidgetItem(loc['name'])
                item.setData(Qt.UserRole, loc)
                list_widget.addItem(item)
            list_widget.show()
            list_widget.setMaximumHeight(200)
        else:
            list_widget.hide()

    def on_start_selected(self, item):
        data = item.data(Qt.UserRole)
        self.start_location = data
        self.start_input.setText(data['name'])
        self.start_suggestions.hide()
        self.update_map_markers()

    def on_dest_selected(self, item):
        data = item.data(Qt.UserRole)
        self.end_location = data
        self.dest_input.setText(data['name'])
        self.dest_suggestions.hide()
        self.update_map_markers()

    def update_map_markers(self):
        if self.start_location:
            self.map_widget.add_start_marker(
                [self.start_location['lat'], self.start_location['lon']], 
                self.start_location['name']
            )
        if self.end_location:
            self.map_widget.add_end_marker(
                [self.end_location['lat'], self.end_location['lon']], 
                self.end_location['name']
            )
            
    def closeEvent(self, event):
        event.accept()