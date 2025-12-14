from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import pyqtSignal
import folium
import io
import json

class CustomWebEnginePage(QWebEnginePage):
    console_message_signal = pyqtSignal(str)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("CLICK:"):
            self.console_message_signal.emit(message)

class MapWidget(QWidget):
    map_clicked_signal = pyqtSignal(float, float) 

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = QWebEngineView()
        self.page = CustomWebEnginePage()
        self.page.console_message_signal.connect(self.handle_js_message)
        self.view.setPage(self.page)
        
        self.layout.addWidget(self.view)
        self.map_obj = None

    def handle_js_message(self, msg):
        try:
            coords = msg.split(":")[1]
            lat_str, lon_str = coords.split(",")
            lat, lon = float(lat_str), float(lon_str)
            self.map_clicked_signal.emit(lat, lon)
        except:
            pass

    def load_map(self, center=[-1.265, 116.831], zoom=13):
        self.map_obj = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB dark_matter")
        
        self.map_obj.get_root().html.add_child(folium.Element("""
            <script>
                window.onload = function() {
                    var maps = [];
                    for (var key in window) {
                        if (key.startsWith('map_')) {
                            var obj = window[key];
                            if (obj && obj.on) {
                                obj.on('click', function(e) {
                                    console.log("CLICK:" + e.latlng.lat + "," + e.latlng.lng);
                                });
                                // Expose map object globally for other JS functions
                                window.my_folium_map = obj;
                            }
                        }
                    }
                };
                
                // Fungsi JS untuk menambah marker sementara tanpa reload
                function js_add_temp_marker(lat, lng) {
                    if (window.my_folium_map) {
                        L.circleMarker([lat, lng], {
                            radius: 4,
                            color: 'yellow',
                            fillColor: 'orange',
                            fillOpacity: 1
                        }).addTo(window.my_folium_map);
                    }
                }
            </script>
        """))

        data = io.BytesIO()
        self.map_obj.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())

    def add_temp_marker_visual(self, lat, lon):
        """Memanggil fungsi JS untuk memunculkan titik visual seketika"""
        js_code = f"js_add_temp_marker({lat}, {lon});"
        self.view.page().runJavaScript(js_code)

    def draw_route(self, coordinates, color="blue"):
        if not self.map_obj: return
        folium.PolyLine(locations=coordinates, color=color, weight=5, opacity=0.8).add_to(self.map_obj)
        self.refresh_view()

    def add_start_marker(self, location, label):
        folium.Marker(location, popup=label, icon=folium.Icon(color="green", icon="play")).add_to(self.map_obj)
        self.refresh_view()

    def add_end_marker(self, location, label):
        folium.Marker(location, popup=label, icon=folium.Icon(color="red", icon="stop")).add_to(self.map_obj)
        self.refresh_view()
    
    def add_flood_polygon(self, points):
        """Menggambar area banjir bentuk bebas (Polygon)"""
        if len(points) < 3: return
        folium.Polygon(
            locations=points,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.4,
            popup="AREA BANJIR (User)"
        ).add_to(self.map_obj)
        self.refresh_view()

    def add_flood_areas(self, flood_data):
        for point in flood_data:
            if 'radius' in point:
                lat, lon = point['latitude'], point['longitude']
                r = point.get('radius', 100)
                folium.Circle([lat, lon], radius=r, color="red", fill=True, fill_opacity=0.4, popup="BANJIR").add_to(self.map_obj)
        self.refresh_view()
        
    def clear_routes(self):
        pass 

    def set_status(self, text):
        pass

    def refresh_view(self):
        data = io.BytesIO()
        self.map_obj.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
