import io
import folium
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.webview = QWebEngineView()
        self.layout.addWidget(self.webview)
        
        self.map = None
        self.default_location = [-1.265, 116.831] 
        
        # --- MEMORY PENYIMPANAN ---
        # Kita simpan data banjir di sini agar tidak hilang saat refresh
        self.stored_flood_data = [] 
        
        self.load_map()

    def load_map(self):
        """Reset peta ke kondisi awal"""
        self.map = folium.Map(
            location=self.default_location, 
            zoom_start=13,
            tiles='CartoDB dark_matter',
            control_scale=True
        )
        
        # Setiap kali load map baru, otomatis gambar ulang banjir (jika ada datanya)
        if self.stored_flood_data:
            self._draw_flood_layers()
            
        self.refresh_map()

    def add_flood_areas(self, flood_data):
        """Simpan data banjir dan gambar"""
        self.stored_flood_data = flood_data # Simpan ke memori
        self._draw_flood_layers()
        self.refresh_map()

    def _draw_flood_layers(self):
        """Fungsi internal untuk menggambar lingkaran merah"""
        if not self.stored_flood_data:
            return

        for point in self.stored_flood_data:
            try:
                lat = point.get('latitude')
                lon = point.get('longitude')
                radius = point.get('radius', 50)
                street = point.get('street', 'Area Banjir')
                
                folium.Circle(
                    location=[lat, lon],
                    radius=radius,
                    color='#ef4444',      # Merah terang
                    fill=True,
                    fill_color='#ef4444',
                    fill_opacity=0.4,
                    popup=f"⛔ BANJIR: {street}"
                ).add_to(self.map)
            except Exception:
                pass

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
        """Menggambar rute tanpa menghapus banjir"""
        # Jangan panggil load_map() di sini agar marker start/end & banjir tidak hilang
        
        if route_coords:
            folium.PolyLine(
                route_coords,
                color=color,
                weight=5,
                opacity=0.8,
                tooltip="Rute Aman"
            ).add_to(self.map)
            
            # Zoom agar rute terlihat jelas
            self.map.fit_bounds(route_coords)
            self.refresh_map()

    def clear_routes(self):
        """Hapus rute tapi pertahankan banjir"""
        # Reload map dasar
        self.load_map() 
        # (Fungsi load_map di atas sudah otomatis menggambar ulang banjir)

    def set_status(self, text):
        print(f"MAP STATUS: {text}")

    def refresh_map(self):
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webview.setHtml(data.getvalue().decode())