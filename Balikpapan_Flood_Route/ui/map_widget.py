import io
import folium
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # WebView untuk menampilkan HTML Peta
        self.webview = QWebEngineView()
        self.layout.addWidget(self.webview)
        
        self.map = None
        self.start_marker = None
        self.end_marker = None
        self.route_line = None
        self.flood_circles = []
        
        # Lokasi Default: Balikpapan
        self.default_location = [-1.265, 116.831] 
        self.load_map()

    def load_map(self):
        """Memuat peta dasar"""
        self.map = folium.Map(
            location=self.default_location, 
            zoom_start=13,
            tiles='CartoDB dark_matter', # Tampilan Gelap biar keren
            control_scale=True
        )
        self.refresh_map()

    def set_status(self, text):
        # Fungsi dummy biar tidak error saat dipanggil main window
        print(f"STATUS MAP: {text}")

    def add_flood_areas(self, flood_data):
        """
        MENGGAMBAR LINGKARAN MERAH (VISUALISASI BANJIR)
        """
        for point in flood_data:
            lat = point.get('latitude')
            lon = point.get('longitude')
            radius = point.get('radius', 50)
            desc = point.get('street', 'Area Banjir')
            depth = point.get('depth', '? cm')

            # Gambar Lingkaran Merah
            folium.Circle(
                location=[lat, lon],
                radius=radius, # dalam meter
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.4,
                popup=f"⛔ BANJIR: {desc}<br>Kedalaman: {depth}"
            ).add_to(self.map)
        
        self.refresh_map()

    def add_start_marker(self, coords, name="Start"):
        folium.Marker(
            location=coords,
            popup=f"Start: {name}",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(self.map)
        self.refresh_map()

    def add_end_marker(self, coords, name="Tujuan"):
        folium.Marker(
            location=coords,
            popup=f"Tujuan: {name}",
            icon=folium.Icon(color='blue', icon='flag')
        ).add_to(self.map)
        self.refresh_map()

    def draw_route(self, route_coords, color='#3b82f6'):
        """Menggambar garis rute"""
        if route_coords:
            folium.PolyLine(
                route_coords,
                color=color,
                weight=5,
                opacity=0.8
            ).add_to(self.map)
            
            # Zoom otomatis agar rute terlihat semua
            self.map.fit_bounds(route_coords)
            self.refresh_map()

    def clear_routes(self):
        # Karena folium susah hapus layer satu per satu secara dinamis di PyQt,
        # cara termudah adalah reload peta dasar, lalu gambar ulang floodnya nanti.
        # (Diimplementasikan sederhana dengan reload map)
        self.load_map()

    def refresh_map(self):
        """Simpan peta ke HTML dan tampilkan di WebView"""
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webview.setHtml(data.getvalue().decode())