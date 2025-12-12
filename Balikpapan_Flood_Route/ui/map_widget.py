from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
import folium
from folium.plugins import Fullscreen, MarkerCluster
import io
import sys
import math

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.map = None
        self.current_routes = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.web_view)
        
        self.status_label = QLabel("Memuat peta Balikpapan...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: rgba(15, 23, 42, 0.95);
            color: #ffffff;
            padding: 8px 16px;
            font-size: 13px;
            border-top: 1px solid #334155;
        """)
        layout.addWidget(self.status_label)
        
    def load_map(self):
        balikpapan_center = [-1.267, 116.827]
        
        self.map = folium.Map(
            location=balikpapan_center,
            zoom_start=13,
            tiles='CartoDB dark_matter',
            width='100%',
            height='100%',
            control_scale=True,
            zoom_control=True,
            min_zoom=11,
            max_zoom=18
        )
        
        balikpapan_bounds = [[-1.35, 116.70], [-1.15, 116.95]]
        self.map.fit_bounds(balikpapan_bounds)
        
        Fullscreen().add_to(self.map)
        
        self.save_and_load_map()
        self.set_status("Peta Balikpapan siap")
        
    def save_and_load_map(self):
        if self.map:
            data = io.BytesIO()
            self.map.save(data, close_file=False)
            html = data.getvalue().decode()
            self.web_view.setHtml(html)
            
    def add_start_marker(self, coords, address=""):
        if self.map:
            popup_text = f"<b>LOKASI AWAL</b><br>{address}" if address else "LOKASI AWAL"
            folium.Marker(
                location=coords,
                popup=popup_text,
                icon=folium.Icon(color='green', icon='play', prefix='fa'),
                tooltip='Lokasi Awal'
            ).add_to(self.map)
            self.save_and_load_map()
            
    def add_end_marker(self, coords, address=""):
        if self.map:
            popup_text = f"<b>LOKASI TUJUAN</b><br>{address}" if address else "LOKASI TUJUAN"
            folium.Marker(
                location=coords,
                popup=popup_text,
                icon=folium.Icon(color='red', icon='flag', prefix='fa'),
                tooltip='Lokasi Tujuan'
            ).add_to(self.map)
            self.save_and_load_map()
            
    def add_route(self, coords_list, color='#3b82f6', name='Rute', weight=5, opacity=0.8):
        if self.map and coords_list and len(coords_list) >= 2:
            folium.PolyLine(
                locations=coords_list,
                color=color,
                weight=weight,
                opacity=opacity,
                popup=f"<b>{name}</b>",
                tooltip=name
            ).add_to(self.map)
            
    def add_multiple_routes(self, routes_data):
        if self.map:
            self.current_routes = []
            
            colors = {
                'teraman': '#10b981',
                'tercepat': '#f59e0b',
                'alternatif_1': '#3b82f6',
                'alternatif_2': '#8b5cf6',
                'alternatif_3': '#ef4444'
            }
            
            for i, route in enumerate(routes_data):
                path = route.get('path', [])
                route_type = route.get('type', 'alternatif_1')
                color = colors.get(route_type, '#3b82f6')
                name = f"Rute {i+1}: {route_type}"
                
                if path and len(path) > 0:
                    coords_list = []
                    for node_id in path:
                        if hasattr(self, 'graph'):
                            coords = self.graph.get_coordinates(node_id)
                            coords_list.append(coords)
                    
                    if coords_list:
                        opacity = 0.9 if i == 0 else 0.7
                        weight = 5 if i == 0 else 4
                        self.add_route(coords_list, color, name, weight, opacity)
                        self.current_routes.append({
                            'coords': coords_list,
                            'color': color,
                            'name': name,
                            'type': route_type
                        })
            
            self.save_and_load_map()
            
    def add_flood_areas(self, flood_data):
        if self.map and flood_data:
            flood_layer = folium.FeatureGroup(name='Area Banjir', show=True)
            
            for flood in flood_data:
                if 'latitude' in flood and 'longitude' in flood:
                    lat = flood['latitude']
                    lon = flood['longitude']
                    
                    radius = flood.get('radius', 30)
                    
                    level = flood.get('level', 'Tinggi')
                    depth = flood.get('depth', '>50cm')
                    affected_street = flood.get('street', 'Jalan utama')
                    
                    popup_html = f"""
                    <div style='font-family: Arial; min-width: 200px;'>
                        <h4 style='color: #ef4444; margin: 0;'>AREA BANJIR</h4>
                        <hr style='margin: 5px 0;'>
                        <p style='margin: 3px 0;'><b>Lokasi:</b> {affected_street}</p>
                        <p style='margin: 3px 0;'><b>Tinggi:</b> {depth}</p>
                        <p style='margin: 3px 0;'><b>Level:</b> {level}</p>
                        <p style='margin: 3px 0;'><b>Radius:</b> {radius}m</p>
                    </div>
                    """
                    
                    folium.Circle(
                        location=[lat, lon],
                        radius=radius,
                        color='#ef4444',
                        fill=True,
                        fill_color='#ef4444',
                        fill_opacity=0.5,
                        weight=2,
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip='Area Banjir - Hati-hati!'
                    ).add_to(flood_layer)
            
            flood_layer.add_to(self.map)
            
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; 
                        width: 160px; height: 80px;
                        background-color: rgba(30, 41, 59, 0.9);
                        border: 2px solid #475569;
                        border-radius: 8px;
                        padding: 10px;
                        font-family: Arial;
                        font-size: 12px;
                        color: white;
                        z-index: 9999;">
                <div style="font-weight: bold; margin-bottom: 5px; color: #ef4444;">LEGENDA</div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 12px; height: 12px; background-color: #ef4444; 
                              border-radius: 50%; margin-right: 8px; opacity: 0.7;"></div>
                    <span>Area Banjir</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px 0;">
                    <div style="width: 12px; height: 12px; background-color: #10b981; 
                              border-radius: 50%; margin-right: 8px;"></div>
                    <span>Rute Aman</span>
                </div>
            </div>
            '''
            
            if self.map:
                self.map.get_root().html.add_child(folium.Element(legend_html))
            
            self.save_and_load_map()
            self.set_status(f"Ditampilkan {len(flood_data)} area banjir")
    
    def clear_map(self):
        self.map = None
        self.current_routes = []
        self.load_map()
        
    def clear_routes(self):
        if self.map:
            self.current_routes = []
            self.save_and_load_map()
        
    def set_status(self, text):
        self.status_label.setText(text)
        
    def set_graph(self, graph):
        self.graph = graph
        
    def cleanup(self):
        self.web_view.deleteLater()