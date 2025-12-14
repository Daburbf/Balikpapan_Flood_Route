from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QSplitter, QLineEdit, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer
import os
import json

# Import Core System
from ui.map_widget import MapWidget
from core.graph import Graph
from core.dijkstra import Dijkstra

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. INISIALISASI PETA & DIGITASI JALAN
        self.graph = Graph() 
        self.dijkstra = Dijkstra(self.graph)
        
        self.flood_data = []
        self.search_data = [] 
        self.start_location = None
        self.end_location = None

        # 2. Load Data Tambahan
        self.init_data()
        self.extract_streets_from_osm() 
        
        # 3. Setup Tampilan
        self.init_ui()
        
    def init_data(self):
        # --- LOAD DATA BANJIR ---
        flood_file = 'flood_data.json'
        if not os.path.exists(flood_file):
            flood_file = os.path.join('data', 'flood_data.json')

        if os.path.exists(flood_file):
            try:
                with open(flood_file, 'r') as f:
                    data = json.load(f)
                    self.flood_data = data.get('flood_points', [])
                    if self.flood_data:
                        print(f"✅ Memuat {len(self.flood_data)} titik banjir.")
                        self.graph.apply_flood_data(self.flood_data)
            except Exception as e:
                print(f"❌ Error JSON: {e}")
        else:
            print(f"⚠️ Warning: File '{flood_file}' tidak ditemukan.")

        # --- DATA LOKASI UMUM ---
        self.search_data = [
            {'name': 'Bandara SAMS Sepinggan', 'lat': -1.268, 'lon': 116.894},
            {'name': 'Plaza Balikpapan', 'lat': -1.262, 'lon': 116.832},
            {'name': 'RSUD Dr. Kanujoso', 'lat': -1.253, 'lon': 116.827},
            {'name': 'Pelabuhan Semayang', 'lat': -1.279, 'lon': 116.807},
            {'name': 'Kantor Walikota BPP', 'lat': -1.263, 'lon': 116.827},
            {'name': 'E-Walk BSB', 'lat': -1.265, 'lon': 116.831},
            {'name': 'Pasar Klandasan', 'lat': -1.270, 'lon': 116.825},
            {'name': 'Lapangan Merdeka', 'lat': -1.275, 'lon': 116.820},
        ]
        
    def extract_streets_from_osm(self):
        print("🔍 Mengindeks nama jalan dari peta... (Agar bisa dicari)")
        try:
            G = self.graph.G
            seen_names = set()
            for u, v, data in G.edges(data=True):
                if 'name' in data:
                    name = data['name']
                    if isinstance(name, list):
                        name = name[0]
                    if name and name not in seen_names:
                        seen_names.add(name)
                        node_data = G.nodes[u]
                        self.search_data.append({
                            'name': str(name),
                            'lat': node_data['y'],
                            'lon': node_data['x']
                        })
            print(f"✅ Berhasil mengindeks {len(seen_names)} nama jalan unik.")
        except Exception as e:
            print(f"⚠️ Gagal mengindeks nama jalan: {e}")

    def init_ui(self):
        self.setWindowTitle("BALIKPAPAN FLOOD SAFE ROUTE (OSM Powered)")
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
        if self.flood_data:
            self.map_widget.add_flood_areas(self.flood_data)
        self.map_widget.set_status(f"Sistem Siap. {len(self.search_data)} lokasi terindeks.")

    def find_route(self):
        if not self.start_location or not self.end_location:
            QMessageBox.warning(self, "Input Kurang", "Pilih Lokasi Awal dan Tujuan dulu.")
            return

        self.map_widget.set_status("Menghitung rute...")
        
        try:
            route_coords = self.dijkstra.find_route(
                self.start_location['lat'], self.start_location['lon'],
                self.end_location['lat'], self.end_location['lon']
            )
            
            if route_coords:
                # Jangan clear routes sembarangan, cukup timpa
                self.map_widget.clear_routes() 
                self.update_map_markers() 
                self.map_widget.draw_route(route_coords, color='#3b82f6')
                self.map_widget.set_status("Rute Aman Ditemukan!")
                self.flood_warning.setText("✅ Rute Aman Tersedia")
                self.flood_warning.setStyleSheet("color: #10b981; font-weight: bold;")
            else:
                QMessageBox.information(self, "Gagal", "Tidak ada jalur aman. Lokasi mungkin terkepung banjir.")
        except Exception as e:
            print(f"Error Routing: {e}")

    def reset_app(self):
        """Fungsi untuk mereset aplikasi ke kondisi awal"""
        # 1. Bersihkan Input Text
        self.start_input.clear()
        self.dest_input.clear()
        
        # 2. Reset Variabel Lokasi
        self.start_location = None
        self.end_location = None
        
        # 3. Reset Status Label
        self.flood_warning.setText("Status: Menunggu")
        self.flood_warning.setStyleSheet("color: white;")
        
        # 4. Bersihkan Peta (Hapus rute & marker, tapi banjhir tetap ada karena map_widget sudah pintar)
        self.map_widget.clear_routes()
        self.map_widget.set_status("Peta direset.")

    # --- UI COMPONENTS ---
    def create_left_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #1e293b; color: white;")
        layout = QVBoxLayout(panel)
        
        layout.addWidget(QLabel("<h2>BALIKPAPAN NAV</h2>"))
        
        # INPUT AWAL
        layout.addWidget(QLabel("Lokasi Awal:"))
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Ketik nama jalan...")
        self.start_input.setStyleSheet("padding: 8px; color: black; border-radius: 4px;")
        layout.addWidget(self.start_input)
        
        self.start_suggestions = QListWidget()
        self.start_suggestions.hide()
        self.start_suggestions.setStyleSheet("color: black; background: white;")
        self.start_suggestions.itemClicked.connect(self.on_start_selected)
        layout.addWidget(self.start_suggestions)

        # INPUT TUJUAN
        layout.addWidget(QLabel("Tujuan:"))
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Ketik nama jalan...")
        self.dest_input.setStyleSheet("padding: 8px; color: black; border-radius: 4px;")
        layout.addWidget(self.dest_input)
        
        self.dest_suggestions = QListWidget()
        self.dest_suggestions.hide()
        self.dest_suggestions.setStyleSheet("color: black; background: white;")
        self.dest_suggestions.itemClicked.connect(self.on_dest_selected)
        layout.addWidget(self.dest_suggestions)

        # JARAK TOMBOL
        layout.addSpacing(20)

        # TOMBOL CARI RUTE
        self.btn_route = QPushButton("🔍 CARI RUTE AMAN")
        self.btn_route.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; 
                padding: 12px; 
                font-weight: bold;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_route.clicked.connect(self.find_route)
        layout.addWidget(self.btn_route)
        
        # TOMBOL RESET (BARU)
        self.btn_reset = QPushButton("🔄 RESET")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #dc2626; 
                padding: 10px; 
                font-weight: bold;
                border-radius: 6px;
                color: white;
                margin-top: 5px;
            }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        self.btn_reset.clicked.connect(self.reset_app)
        layout.addWidget(self.btn_reset)
        
        layout.addSpacing(20)
        self.flood_warning = QLabel("Status: Menunggu")
        layout.addWidget(self.flood_warning)
        layout.addStretch()
        
        # Connect Search
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

    # --- LOGIKA SEARCH ---
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