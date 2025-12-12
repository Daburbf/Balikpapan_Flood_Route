from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFrame, QScrollArea, QRadioButton, QButtonGroup, QDialog, QMessageBox, QGroupBox
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

class SearchWidget(QWidget):
    location_selected = pyqtSignal(dict)
    
    def __init__(self, title, placeholder, is_destination=False):
        super().__init__()
        self.title = title
        self.placeholder = placeholder
        self.is_destination = is_destination
        self.search_results = []
        self.all_locations = self.load_all_locations()
        self.setup_ui()
    
    def load_all_locations(self):
        import json
        import os
        
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'balikpapan_locations.json')
        try:
            with open(file_path, 'r') as f:
                location_data = json.load(f)
                return location_data.get('locations', [])
        except:
            return []
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff; margin-bottom: 2px;")
        
        if not self.is_destination:
            history_btn = QPushButton("Riwayat")
            history_btn.setCursor(Qt.PointingHandCursor)
            history_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            history_btn.clicked.connect(self.show_history_dialog)
            header_layout.addStretch()
            header_layout.addWidget(history_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.placeholder)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                border: 2px solid #475569;
                border-radius: 10px;
                padding: 12px 14px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)
        
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setVisible(False)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1e293b;
                border: 1px solid #475569;
                border-radius: 8px;
                margin-top: 4px;
            }
            QScrollBar:vertical {
                background-color: #0f172a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 4px;
            }
        """)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignTop)
        self.results_layout.setSpacing(2)
        self.results_scroll.setWidget(self.results_container)
        
        if not self.is_destination:
            transport_group = QGroupBox("Pilih Kendaraan")
            transport_group.setStyleSheet("""
                QGroupBox {
                    color: #ffffff;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    margin-top: 10px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 6px;
                    color: #ffffff;
                }
            """)
            
            transport_layout = QHBoxLayout(transport_group)
            transport_layout.setContentsMargins(12, 20, 12, 12)
            
            self.transport_group = QButtonGroup(self)
            
            self.car_radio = QRadioButton("Mobil")
            self.motor_radio = QRadioButton("Motor")
            self.walk_radio = QRadioButton("Jalan Kaki")
            
            self.car_radio.setChecked(True)
            
            radio_style = """
                QRadioButton {
                    color: #ffffff;
                    font-size: 13px;
                    padding: 4px 8px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QRadioButton::indicator::unchecked {
                    border: 2px solid #64748b;
                    border-radius: 8px;
                }
                QRadioButton::indicator::checked {
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                    background-color: #3b82f6;
                }
            """
            
            for radio in [self.car_radio, self.motor_radio, self.walk_radio]:
                radio.setStyleSheet(radio_style)
                transport_layout.addWidget(radio)
                self.transport_group.addButton(radio)
            
            transport_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_scroll)
        
        if not self.is_destination:
            layout.addWidget(transport_group)
    
    def on_search_text_changed(self, text):
        if text.strip():
            self.perform_search(text)
            self.results_scroll.setVisible(True)
        else:
            self.clear_results()
            self.results_scroll.setVisible(False)
    
    def perform_search(self, query):
        self.clear_results()
        
        if not self.all_locations:
            return
        
        query_lower = query.lower()
        matches = []
        
        for location in self.all_locations:
            name = location.get('name', '').lower()
            address = location.get('address', '').lower()
            
            if query_lower in name or query_lower in address:
                matches.append(location)
        
        self.search_results = matches[:10]
        
        if self.search_results:
            self.display_results()
            self.results_scroll.setVisible(True)
        else:
            no_result = QLabel("Tidak ditemukan")
            no_result.setAlignment(Qt.AlignCenter)
            no_result.setStyleSheet("color: #94a3b8; padding: 20px;")
            self.results_layout.addWidget(no_result)
    
    def display_results(self):
        for location in self.search_results:
            result_item = self.create_result_item(location)
            self.results_layout.addWidget(result_item)
    
    def create_result_item(self, location):
        item_widget = QWidget()
        item_widget.setCursor(Qt.PointingHandCursor)
        item_widget.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                margin: 2px;
            }
            QWidget:hover {
                background-color: #1e293b;
                border: 1px solid #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(item_widget)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
        name_label = QLabel(location.get('name', 'Unknown'))
        name_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff;")
        
        address_label = QLabel(location.get('address', ''))
        address_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        address_label.setWordWrap(True)
        
        layout.addWidget(name_label)
        layout.addWidget(address_label)
        
        item_widget.mousePressEvent = lambda e, loc=location: self.select_location(loc)
        
        return item_widget
    
    def select_location(self, location):
        self.search_input.setText(location.get('name', ''))
        self.clear_results()
        self.results_scroll.setVisible(False)
        self.location_selected.emit(location)
    
    def clear_results(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def get_selected_transport(self):
        if not hasattr(self, 'transport_group'):
            return 'car'
        
        if self.car_radio.isChecked():
            return 'car'
        elif self.motor_radio.isChecked():
            return 'motor'
        elif self.walk_radio.isChecked():
            return 'walk'
        return 'car'
    
    def clear(self):
        self.search_input.clear()
        self.clear_results()
        self.results_scroll.setVisible(False)
        if hasattr(self, 'car_radio'):
            self.car_radio.setChecked(True)
    
    def show_history_dialog(self):
        from ui.history_dialog import HistoryDialog
        dialog = HistoryDialog(self)
        dialog.location_selected.connect(self.on_history_location_selected)
        dialog.exec_()
    
    def on_history_location_selected(self, location_text):
        self.search_input.setText(location_text)
        self.perform_search(location_text)
        self.results_scroll.setVisible(True)