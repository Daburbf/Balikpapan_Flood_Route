from PyQt5.QtGui import QFont

class StyleManager:
    @staticmethod
    def get_modern_style():
        style = """
        QMainWindow {
            background-color: #0f172a;
        }
        
        QWidget {
            background-color: #1e293b;
            color: #e2e8f0;
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }
        
        QFrame#card {
            background-color: #334155;
            border-radius: 16px;
            border: 1px solid #475569;
        }
        
        QLineEdit {
            background-color: rgba(30, 41, 59, 0.8);
            border: 2px solid #475569;
            border-radius: 12px;
            padding: 14px 20px;
            color: #f1f5f9;
            font-size: 14px;
            font-weight: 500;
            selection-background-color: #3b82f6;
        }
        
        QLineEdit:focus {
            border: 2px solid #3b82f6;
            background-color: rgba(30, 41, 59, 0.9);
        }
        
        QLineEdit::placeholder {
            color: #94a3b8;
            font-weight: 400;
        }
        
        QPushButton {
            background-color: #3b82f6;
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.3px;
        }
        
        QPushButton:hover {
            background-color: #2563eb;
        }
        
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        
        QPushButton#primary {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3b82f6, stop:1 #8b5cf6);
        }
        
        QPushButton#danger {
            background-color: #ef4444;
        }
        
        QPushButton#danger:hover {
            background-color: #dc2626;
        }
        
        QComboBox {
            background-color: rgba(30, 41, 59, 0.8);
            border: 2px solid #475569;
            border-radius: 12px;
            padding: 12px 20px;
            color: #f1f5f9;
            font-size: 14px;
            min-height: 48px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 40px;
        }
        
        QComboBox::down-arrow {
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #94a3b8;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1e293b;
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 8px;
            selection-background-color: #3b82f6;
            selection-color: white;
        }
        
        QLabel {
            color: #e2e8f0;
            font-size: 13px;
            font-weight: 500;
        }
        
        QLabel#title {
            font-size: 28px;
            font-weight: 800;
            color: #3b82f6;
        }
        
        QLabel#subtitle {
            font-size: 13px;
            color: #94a3b8;
            font-weight: 400;
        }
        
        QLabel#distance {
            font-size: 32px;
            font-weight: 800;
            color: #3b82f6;
        }
        
        QLabel#time {
            font-size: 24px;
            font-weight: 700;
            color: #10b981;
        }
        
        QListWidget {
            background-color: transparent;
            border: 2px solid #475569;
            border-radius: 12px;
            font-size: 13px;
            color: #e2e8f0;
            outline: none;
        }
        
        QListWidget::item {
            padding: 12px 16px;
            border-bottom: 1px solid #334155;
            background-color: transparent;
        }
        
        QListWidget::item:selected {
            background-color: rgba(59, 130, 246, 0.2);
            border-radius: 8px;
            border: none;
        }
        
        QListWidget::item:hover {
            background-color: rgba(59, 130, 246, 0.1);
            border-radius: 8px;
        }
        
        QScrollBar:vertical {
            background-color: transparent;
            width: 8px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #475569;
            border-radius: 4px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #64748b;
        }
        
        QProgressBar {
            border: 2px solid #475569;
            border-radius: 8px;
            text-align: center;
            color: white;
            background-color: transparent;
            height: 6px;
        }
        
        QProgressBar::chunk {
            background-color: #3b82f6;
            border-radius: 8px;
        }
        
        QGroupBox {
            border: none;
            margin-top: 20px;
            font-weight: 700;
            font-size: 14px;
            color: #94a3b8;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 0;
            padding: 0 8px 8px 0;
        }
        
        QFrame#separator {
            background-color: #475569;
            border: none;
            max-height: 1px;
            min-height: 1px;
        }
        
        QTabWidget::pane {
            border: 2px solid #475569;
            border-radius: 12px;
            background-color: transparent;
        }
        
        QTabBar::tab {
            background-color: #334155;
            color: #94a3b8;
            padding: 12px 24px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }
        
        QTabBar::tab:selected {
            background-color: #3b82f6;
            color: white;
        }
        
        QTabBar::tab:hover {
            background-color: #475569;
        }
        
        QCheckBox {
            color: #e2e8f0;
            font-size: 13px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 6px;
            border: 2px solid #475569;
        }
        
        QCheckBox::indicator:checked {
            background-color: #3b82f6;
            border: 2px solid #3b82f6;
        }
        
        QRadioButton {
            color: #e2e8f0;
            font-size: 13px;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid #475569;
        }
        
        QRadioButton::indicator:checked {
            background-color: #3b82f6;
            border: 2px solid #3b82f6;
        }
        
        QToolTip {
            background-color: #1e293b;
            color: #e2e8f0;
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 8px;
        }
        
        QStatusBar {
            background-color: #0f172a;
            color: #94a3b8;
            border-top: 1px solid #475569;
            font-size: 11px;
        }
        """
        return style
    
    @staticmethod
    def setup_font():
        font = QFont("Segoe UI", 10)
        font.setWeight(QFont.Normal)
        return font