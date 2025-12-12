from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QWidget, QFrame, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class HistoryDialog(QDialog):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Riwayat Pencarian Rute")
        self.setGeometry(300, 200, 500, 600)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1e293b;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header_label = QLabel("RIWAYAT PENCARIAN")
        header_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #3b82f6;")
        layout.addWidget(header_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #334155;")
        layout.addWidget(separator)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #334155;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #64748b;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(10)
        
        history_items = self.history_manager.get_recent_history(20)
        
        if not history_items:
            no_history_label = QLabel("Belum ada riwayat pencarian")
            no_history_label.setStyleSheet("color: #94a3b8; font-style: italic; padding: 20px;")
            scroll_layout.addWidget(no_history_label)
        else:
            for item in history_items:
                history_widget = self.create_history_item(item)
                scroll_layout.addWidget(history_widget)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        
        clear_btn = QPushButton("HAPUS RIWAYAT")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        
        close_btn = QPushButton("TUTUP")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(close_btn)
        layout.addWidget(buttons_widget)
        
    def create_history_item(self, item):
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #334155;
                border-radius: 8px;
                border: 1px solid #475569;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        timestamp_label = QLabel(item.get('timestamp', 'Unknown'))
        timestamp_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        
        route_type = item.get('route', {}).get('route_type', 'unknown')
        type_label = QLabel(route_type.upper())
        type_label.setStyleSheet("""
            color: #ffffff;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 10px;
            background-color: #3b82f6;
        """)
        
        header_layout.addWidget(timestamp_label)
        header_layout.addStretch()
        header_layout.addWidget(type_label)
        
        start_label = QLabel(f"Dari: {item.get('start', {}).get('name', 'Unknown')}")
        start_label.setStyleSheet("color: #ffffff; font-size: 13px;")
        
        end_label = QLabel(f"Ke: {item.get('end', {}).get('name', 'Unknown')}")
        end_label.setStyleSheet("color: #ffffff; font-size: 13px;")
        
        route_info = item.get('route', {})
        distance = route_info.get('distance', 0)
        time_estimate = route_info.get('time_estimate', 0)
        has_flood = route_info.get('has_flood', False)
        
        info_text = f"Jarak: {self.format_distance(distance)} - Waktu: {time_estimate} min"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        
        if has_flood:
            flood_label = QLabel("Melewati area banjir")
            flood_label.setStyleSheet("color: #f59e0b; font-size: 11px;")
        else:
            flood_label = QLabel("Aman dari banjir")
            flood_label.setStyleSheet("color: #10b981; font-size: 11px;")
        
        layout.addWidget(header_widget)
        layout.addWidget(start_label)
        layout.addWidget(end_label)
        layout.addWidget(info_label)
        layout.addWidget(flood_label)
        
        return widget
    
    def format_distance(self, distance_meters):
        if distance_meters < 1000:
            return f"{distance_meters:.0f} m"
        else:
            return f"{distance_meters/1000:.1f} km"
    
    def clear_history(self):
        self.history_manager.clear_history()
        self.close()
        QDialog.accept(self)