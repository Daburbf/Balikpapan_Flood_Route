from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox, QSplitter, QSizePolicy, QGroupBox, QRadioButton, QButtonGroup, QLineEdit, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import os
import json

from ui.map_widget import MapWidget
from ui.history_dialog import HistoryDialog
from core.graph import Graph
from core.dijkstra import Dijkstra
from utils.route_calculator import RouteCalculator
from utils.history_manager import HistoryManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.graph = Graph()
        self.dijkstra = None
        self.flood_data = []
        self.street_data = []
        self.common_locations = []
        self.current_routes = []
        self.start_location = None
        self.end_location = None
        self.selected_route_index = 0
        self.history_manager = HistoryManager()
        self.route_calculator = RouteCalculator()
        self.init_data()
        self.init_ui()
        
    def init_data(self):
        try:
            data_dir = 'data'
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            flood_file = os.path.join(data_dir, 'flood_data.json')
            if os.path.exists(flood_file):
                with open(flood_file, 'r') as f:
                    data = json.load(f)
                    self.flood_data = data.get('flood_points', [])
                    print(f"Loaded {len(self.flood_data)} flood points")
            else:
                self.flood_data = self.create_default_flood_data()
                print("Created default flood data")
        except Exception as e:
            print(f"Error loading flood data: {e}")
            self.flood_data = self.create_default_flood_data()
        
        try:
            street_file = os.path.join(data_dir, 'street_data.json')
            if os.path.exists(street_file):
                with open(street_file, 'r') as f:
                    data = json.load(f)
                    self.street_data = data.get('streets', [])
                    print(f"Loaded {len(self.street_data)} streets")
            else:
                self.street_data = self.create_default_street_data()
                print("Created default street data")
        except Exception as e:
            print(f"Error loading street data: {e}")
            self.street_data = self.create_default_street_data()
        
        self.common_locations = self.create_common_locations()
        self.initialize_graph()
        
    def create_default_flood_data(self):
        return [
            {
                "id": 1,
                "latitude": -1.268,
                "longitude": 116.830,
                "street": "Jalan Sudirman",
                "level": "Tinggi",
                "depth": "70cm",
                "radius": 40
            },
            {
                "id": 2,
                "latitude": -1.272,
                "longitude": 116.835,
                "street": "Jalan MT Haryono",
                "level": "Sedang",
                "depth": "40cm",
                "radius": 35
            },
            {
                "id": 3,
                "latitude": -1.265,
                "longitude": 116.828,
                "street": "Jalan Yos Sudarso",
                "level": "Rendah",
                "depth": "20cm",
                "radius": 30
            }
        ]
    
    def create_default_street_data(self):
        return [
            {
                "id": 1,
                "name": "Jalan Sudirman",
                "latitude": -1.268,
                "longitude": 116.830,
                "connections": [2, 3]
            },
            {
                "id": 2,
                "name": "Jalan MT Haryono",
                "latitude": -1.272,
                "longitude": 116.835,
                "connections": [1, 4, 5]
            },
            {
                "id": 3,
                "name": "Jalan Yos Sudarso",
                "latitude": -1.265,
                "longitude": 116.828,
                "connections": [1, 6]
            },
            {
                "id": 4,
                "name": "Jalan A Yani",
                "latitude": -1.275,
                "longitude": 116.838,
                "connections": [2, 7]
            },
            {
                "id": 5,
                "name": "Jalan S Parman",
                "latitude": -1.270,
                "longitude": 116.840,
                "connections": [2, 8]
            },
            {
                "id": 6,
                "name": "Jalan Pranoto",
                "latitude": -1.260,
                "longitude": 116.825,
                "connections": [3, 9]
            },
            {
                "id": 7,
                "name": "Jalan Mulawarman",
                "latitude": -1.280,
                "longitude": 116.835,
                "connections": [4, 10]
            },
            {
                "id": 8,
                "name": "Jalan Ahmad Yani II",
                "latitude": -1.268,
                "longitude": 116.845,
                "connections": [5, 11]
            },
            {
                "id": 9,
                "name": "Jalan Gunung Guntur",
                "latitude": -1.258,
                "longitude": 116.820,
                "connections": [6, 12]
            },
            {
                "id": 10,
                "name": "Jalan Jenderal Sudirman II",
                "latitude": -1.285,
                "longitude": 116.830,
                "connections": [7]
            },
            {
                "id": 11,
                "name": "Jalan Marsma R Iswahyudi",
                "latitude": -1.265,
                "longitude": 116.850,
                "connections": [8]
            },
            {
                "id": 12,
                "name": "Jalan Gunung Merbabu",
                "latitude": -1.255,
                "longitude": 116.815,
                "connections": [9]
            }
        ]
    
    def create_common_locations(self):
        return [
            {'name': 'Bandara Sultan Aji Muhammad Sulaiman', 'latitude': -1.268, 'longitude': 116.894, 'type': 'airport'},
            {'name': 'Mall Balikpapan', 'latitude': -1.262, 'longitude': 116.832, 'type': 'mall'},
            {'name': 'RSUD Dr. Kanujoso', 'latitude': -1.253, 'longitude': 116.827, 'type': 'hospital'},
            {'name': 'Pelabuhan Semayang', 'latitude': -1.279, 'longitude': 116.807, 'type': 'port'},
            {'name': 'Kantor Walikota Balikpapan', 'latitude': -1.263, 'longitude': 116.827, 'type': 'government'},
            {'name': 'Balikpapan Superblock', 'latitude': -1.265, 'longitude': 116.831, 'type': 'commercial'},
            {'name': 'Universitas Balikpapan', 'latitude': -1.258, 'longitude': 116.837, 'type': 'education'},
            {'name': 'Pasar Klandasan', 'latitude': -1.270, 'longitude': 116.825, 'type': 'market'},
            {'name': 'Balaikota Baru', 'latitude': -1.260, 'longitude': 116.840, 'type': 'government'},
            {'name': 'Taman Bekapai', 'latitude': -1.267, 'longitude': 116.829, 'type': 'park'},
            {'name': 'Pantai Kemala', 'latitude': -1.280, 'longitude': 116.820, 'type': 'beach'},
            {'name': 'Kawasan Industri Kariangau', 'latitude': -1.290, 'longitude': 116.790, 'type': 'industrial'}
        ]
        
    def initialize_graph(self):
        self.graph = Graph()
        
        for street in self.street_data:
            node_id = street['id']
            coordinates = (street['latitude'], street['longitude'])
            self.graph.add_node(node_id, coordinates)
        
        for street in self.street_data:
            node_id = street['id']
            connections = street.get('connections', [])
            for connected_id in connections:
                if connected_id in self.graph.nodes:
                    self.graph.add_edge(node_id, connected_id)
        
        if self.flood_data:
            self.graph.set_flood_points(self.flood_data)
            print(f"Set {len(self.flood_data)} flood points in graph")
        
        self.dijkstra = Dijkstra(self.graph)
        print("Graph initialized with", len(self.graph.nodes), "nodes and", 
              sum(len(edges) for edges in self.graph.edges.values())//2, "edges")
        
    def init_ui(self):
        self.setWindowTitle("BALIKPAPAN FLOOD SAFE ROUTE")
        self.setGeometry(100, 50, 1400, 900)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #ffffff;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 1000])
        splitter.setStyleSheet("QSplitter::handle { background-color: #334155; width: 1px; }")
        
        main_layout.addWidget(splitter)
        
        QTimer.singleShot(100, self.initialize_map)
        
    def create_left_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #1e293b;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("BALIKPAPAN FLOOD SAFE ROUTE")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #3b82f6;
            padding: 10px 0;
        """)
        header_layout.addWidget(title_label)
        
        layout.addWidget(header_widget)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #334155;")
        layout.addWidget(separator)
        
        transport_widget = QWidget()
        transport_layout = QVBoxLayout(transport_widget)
        transport_layout.setContentsMargins(0, 0, 0, 0)
        transport_layout.setSpacing(8)
        
        transport_title = QLabel("JENIS TRANSPORTASI")
        transport_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
        """)
        
        self.transport_group = QButtonGroup(self)
        
        self.car_radio = QRadioButton("Mobil")
        self.motor_radio = QRadioButton("Motor")
        self.walk_radio = QRadioButton("Jalan Kaki")
        
        self.car_radio.setChecked(True)
        
        radio_style = """
            QRadioButton {
                color: #ffffff;
                font-size: 14px;
                padding: 8px 12px;
                background-color: #334155;
                border-radius: 6px;
                margin: 2px 0;
            }
            QRadioButton:hover {
                background-color: #475569;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
            }
            QRadioButton::indicator:checked {
                background-color: #3b82f6;
                border: 4px solid #334155;
            }
        """
        
        for radio in [self.car_radio, self.motor_radio, self.walk_radio]:
            radio.setStyleSheet(radio_style)
            transport_layout.addWidget(radio)
            self.transport_group.addButton(radio)
        
        transport_layout.addWidget(transport_title)
        transport_layout.addWidget(self.car_radio)
        transport_layout.addWidget(self.motor_radio)
        transport_layout.addWidget(self.walk_radio)
        
        layout.addWidget(transport_widget)
        
        start_section = QWidget()
        start_layout = QVBoxLayout(start_section)
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.setSpacing(8)
        
        start_title = QLabel("LOKASI AWAL")
        start_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
        """)
        
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Masukkan lokasi awal atau klik peta...")
        self.start_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 10px 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
        
        self.start_suggestions = QListWidget()
        self.start_suggestions.setStyleSheet("""
            QListWidget {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                max-height: 200px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #475569;
            }
            QListWidget::item:hover {
                background-color: #3b82f6;
            }
            QListWidget::item:selected {
                background-color: #2563eb;
            }
        """)
        self.start_suggestions.hide()
        self.start_suggestions.itemClicked.connect(self.on_start_suggestion_selected)
        
        start_layout.addWidget(start_title)
        start_layout.addWidget(self.start_input)
        start_layout.addWidget(self.start_suggestions)
        layout.addWidget(start_section)
        
        dest_section = QWidget()
        dest_layout = QVBoxLayout(dest_section)
        dest_layout.setContentsMargins(0, 0, 0, 0)
        dest_layout.setSpacing(8)
        
        dest_title = QLabel("TUJUAN")
        dest_title.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
        """)
        
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Masukkan lokasi tujuan atau klik peta...")
        self.dest_input.setStyleSheet("""
            QLineEdit {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 10px 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
        
        self.dest_suggestions = QListWidget()
        self.dest_suggestions.setStyleSheet("""
            QListWidget {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                color: white;
                font-size: 13px;
                max-height: 200px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #475569;
            }
            QListWidget::item:hover {
                background-color: #3b82f6;
            }
            QListWidget::item:selected {
                background-color: #2563eb;
            }
        """)
        self.dest_suggestions.hide()
        self.dest_suggestions.itemClicked.connect(self.on_dest_suggestion_selected)
        
        dest_layout.addWidget(dest_title)
        dest_layout.addWidget(self.dest_input)
        dest_layout.addWidget(self.dest_suggestions)
        layout.addWidget(dest_section)
        
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        self.find_route_btn = QPushButton("CARI RUTE")
        self.find_route_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        self.find_route_btn.clicked.connect(self.find_route)
        self.find_route_btn.setCursor(Qt.PointingHandCursor)
        
        self.clear_btn = QPushButton("HAPUS")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_map)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        
        buttons_layout.addWidget(self.find_route_btn)
        buttons_layout.addWidget(self.clear_btn)
        layout.addWidget(buttons_widget)
        
        route_info = self.create_route_info()
        layout.addWidget(route_info)
        
        layout.addStretch()
        
        self.start_input.textChanged.connect(self.on_start_text_changed)
        self.dest_input.textChanged.connect(self.on_dest_text_changed)
        
        return panel
        
    def create_route_info(self):
        route_widget = QWidget()
        route_layout = QVBoxLayout(route_widget)
        route_layout.setContentsMargins(0, 0, 0, 0)
        route_layout.setSpacing(12)
        
        route_title = QLabel("INFORMASI RUTE")
        route_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        
        distance_widget = QWidget()
        distance_layout = QHBoxLayout(distance_widget)
        distance_layout.setContentsMargins(0, 0, 0, 0)
        
        distance_label = QLabel("Jarak:")
        distance_label.setStyleSheet("font-size: 14px; color: #94a3b8;")
        
        self.distance_value = QLabel("--")
        self.distance_value.setStyleSheet("font-size: 20px; font-weight: 700; color: #3b82f6; margin-left: 10px;")
        
        distance_layout.addWidget(distance_label)
        distance_layout.addWidget(self.distance_value)
        distance_layout.addStretch()
        
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        time_label = QLabel("Waktu:")
        time_label.setStyleSheet("font-size: 14px; color: #94a3b8;")
        
        self.time_value = QLabel("--")
        self.time_value.setStyleSheet("font-size: 20px; font-weight: 700; color: #60a5fa; margin-left: 10px;")
        
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_value)
        time_layout.addStretch()
        
        self.flood_warning = QLabel("Status: Belum ada rute")
        self.flood_warning.setStyleSheet("""
            font-size: 12px;
            color: #94a3b8;
            padding: 8px 12px;
            background-color: rgba(148, 163, 184, 0.1);
            border-radius: 6px;
            border: 1px solid rgba(148, 163, 184, 0.3);
            margin-top: 5px;
        """)
        
        route_layout.addWidget(route_title)
        route_layout.addWidget(distance_widget)
        route_layout.addWidget(time_widget)
        route_layout.addWidget(self.flood_warning)
        
        return route_widget
        
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.history_btn = QPushButton("RIWAYAT")
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
        """)
        self.history_btn.clicked.connect(self.show_history)
        self.history_btn.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(left_spacer)
        header_layout.addWidget(self.history_btn)
        
        layout.addWidget(header_widget)
        
        self.map_widget = MapWidget()
        layout.addWidget(self.map_widget)
        
        return panel
        
    def show_history(self):
        history_dialog = HistoryDialog(self.history_manager, self)
        history_dialog.exec_()
        
    def on_start_text_changed(self, text):
        if len(text) >= 2:
            suggestions = self.get_location_suggestions(text)
            if suggestions:
                self.show_suggestions(self.start_suggestions, suggestions)
            else:
                self.start_suggestions.hide()
        else:
            self.start_suggestions.hide()

    def on_dest_text_changed(self, text):
        if len(text) >= 2:
            suggestions = self.get_location_suggestions(text)
            if suggestions:
                self.show_suggestions(self.dest_suggestions, suggestions)
            else:
                self.dest_suggestions.hide()
        else:
            self.dest_suggestions.hide()

    def get_location_suggestions(self, query):
        query = query.lower()
        suggestions = []
        
        for street in self.street_data:
            if query in street.get('name', '').lower():
                suggestions.append({
                    'name': street['name'],
                    'latitude': street['latitude'],
                    'longitude': street['longitude'],
                    'type': 'street'
                })
        
        for loc in self.common_locations:
            if query in loc['name'].lower():
                suggestions.append({
                    'name': loc['name'],
                    'latitude': loc['latitude'],
                    'longitude': loc['longitude'],
                    'type': loc['type']
                })
        
        return suggestions[:8]

    def show_suggestions(self, list_widget, suggestions):
        list_widget.clear()
        for suggestion in suggestions:
            item_text = f"{suggestion['name']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, suggestion)
            list_widget.addItem(item)
        list_widget.show()
        list_widget.setMaximumHeight(min(200, len(suggestions) * 40))

    def on_start_suggestion_selected(self, item):
        location = item.data(Qt.UserRole)
        self.start_input.setText(location['name'])
        self.start_location = location
        self.start_suggestions.hide()
        self.update_map_markers()

    def on_dest_suggestion_selected(self, item):
        location = item.data(Qt.UserRole)
        self.dest_input.setText(location['name'])
        self.end_location = location
        self.dest_suggestions.hide()
        self.update_map_markers()

    def get_selected_transport(self):
        if self.car_radio.isChecked():
            return 'car'
        elif self.motor_radio.isChecked():
            return 'motor'
        elif self.walk_radio.isChecked():
            return 'walk'
        return 'car'

    def on_start_location_selected(self, location):
        self.start_location = location
        if location and 'name' in location:
            name = location['name']
            if len(name) > 30:
                name = name[:27] + "..."
            self.start_input.setText(name)
        
    def on_end_location_selected(self, location):
        self.end_location = location
        if location and 'name' in location:
            name = location['name']
            if len(name) > 30:
                name = name[:27] + "..."
            self.dest_input.setText(name)
        
    def update_map_markers(self):
        if self.start_location:
            coords = (self.start_location['latitude'], self.start_location['longitude'])
            address = self.start_location.get('name', '')
            self.map_widget.add_start_marker(coords, address)
            
        if self.end_location:
            coords = (self.end_location['latitude'], self.end_location['longitude'])
            address = self.end_location.get('name', '')
            self.map_widget.add_end_marker(coords, address)
            
    def find_route(self):
        if not self.start_location or not self.end_location:
            QMessageBox.warning(self, "Informasi Tidak Lengkap", "Silakan pilih lokasi awal dan tujuan.")
            return
            
        start_coords = (self.start_location['latitude'], self.start_location['longitude'])
        end_coords = (self.end_location['latitude'], self.end_location['longitude'])
        
        start_node = self.find_nearest_node(start_coords)
        end_node = self.find_nearest_node(end_coords)
        
        if not start_node or not end_node:
            QMessageBox.warning(self, "Error Rute", "Tidak dapat menemukan rute antara lokasi yang dipilih.")
            return
        
        self.calculate_route(start_node, end_node)
        
    def find_nearest_node(self, coordinates):
        nearest_node = None
        min_distance = float('inf')
        
        for street in self.street_data:
            node_coords = (street['latitude'], street['longitude'])
            distance = RouteCalculator.calculate_distance(node_coords, coordinates)
            
            if distance < min_distance:
                min_distance = distance
                nearest_node = street['id']
                
        print(f"Nearest node found: {nearest_node}, distance: {min_distance:.1f}m")
        return nearest_node
        
    def calculate_route(self, start_node, end_node):
        try:
            print(f"Calculating route from {start_node} to {end_node}")
            
            self.map_widget.clear_map()
            
            if self.flood_data:
                self.map_widget.add_flood_areas(self.flood_data)
                
            start_coords = self.graph.get_coordinates(start_node)
            end_coords = self.graph.get_coordinates(end_node)
            
            self.map_widget.add_start_marker(start_coords, self.start_location.get('name', ''))
            self.map_widget.add_end_marker(end_coords, self.end_location.get('name', ''))
            
            routes = self.dijkstra.find_best_routes(start_node, end_node, max_routes=3)
            print(f"Found {len(routes)} routes")
                
            if not routes:
                QMessageBox.warning(self, "Rute Tidak Ditemukan", "Tidak ada rute yang tersedia.")
                return
                
            self.current_routes = routes
            self.map_widget.set_graph(self.graph)
            self.map_widget.add_multiple_routes(routes)
                
            self.selected_route_index = 0
            self.display_route_info(0)
            
        except Exception as e:
            print(f"Error in calculate_route: {e}")
            QMessageBox.critical(self, "Error Perhitungan", f"Error: {str(e)}")
                
    def display_route_info(self, route_index):
        if not self.current_routes or route_index >= len(self.current_routes):
            return
        
        route = self.current_routes[route_index]
        path = route['path']
        total_distance = route['distance']
        
        has_flood = route.get('has_flood', False)
        
        transport_type = self.get_selected_transport()
        time_estimate = self.route_calculator.estimate_travel_time(total_distance, transport_type, has_flood)
        
        formatted_distance = RouteCalculator.format_distance(total_distance)
        self.distance_value.setText(formatted_distance)
        
        transport_icons = {
            'car': 'Mobil',
            'motor': 'Motor',
            'walk': 'Jalan Kaki'
        }
        transport_name = transport_icons.get(transport_type, 'Mobil')
        self.time_value.setText(f"{transport_name}: {time_estimate} min")
        
        route_type = route.get('type', 'rute')
        if has_flood:
            self.flood_warning.setText(f"Rute melewati area banjir ({route_type})")
            self.flood_warning.setStyleSheet("""
                font-size: 12px;
                color: #f59e0b;
                padding: 8px 12px;
                background-color: rgba(245, 158, 11, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(245, 158, 11, 0.3);
                margin-top: 5px;
            """)
        else:
            self.flood_warning.setText(f"Rute aman dari banjir ({route_type})")
            self.flood_warning.setStyleSheet("""
                font-size: 12px;
                color: #10b981;
                padding: 8px 12px;
                background-color: rgba(16, 185, 129, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(16, 185, 129, 0.3);
                margin-top: 5px;
            """)
            
        route_data = {
            'distance': total_distance,
            'time_estimate': time_estimate,
            'has_flood': has_flood,
            'path': path,
            'route_type': route.get('type', 'unknown')
        }
        
        self.history_manager.add_route_search(self.start_location, self.end_location, route_data)
        
        self.map_widget.set_status(f"Rute ditemukan: {formatted_distance} - {time_estimate} menit - {len(self.current_routes)} alternatif")
            
    def clear_map(self):
        self.map_widget.clear_map()
        self.start_input.clear()
        self.dest_input.clear()
        self.start_location = None
        self.end_location = None
        self.current_routes = []
        
        self.distance_value.setText("--")
        self.time_value.setText("--")
        self.flood_warning.setText("Status: Belum ada rute")
        self.flood_warning.setStyleSheet("""
            font-size: 12px;
            color: #94a3b8;
            padding: 8px 12px;
            background-color: rgba(148, 163, 184, 0.1);
            border-radius: 6px;
            border: 1px solid rgba(148, 163, 184, 0.3);
            margin-top: 5px;
        """)
        
        if self.flood_data:
            self.map_widget.add_flood_areas(self.flood_data)
            
        self.map_widget.set_status("Siap untuk navigasi")
        
    def initialize_map(self):
        self.map_widget.load_map()
        if self.flood_data:
            self.map_widget.add_flood_areas(self.flood_data)
        
        self.map_widget.set_status("Peta Balikpapan - Sistem Navigasi Banjir")
        
    def closeEvent(self, event):
        if hasattr(self.map_widget, 'cleanup'):
            self.map_widget.cleanup()
        event.accept()