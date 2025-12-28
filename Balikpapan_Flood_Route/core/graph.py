import osmnx as ox
import networkx as nx

class Graph:
    def __init__(self):
       
        print("Memuat Peta Balikpapan... (Harap Tunggu)")
        self.G = ox.graph_from_place("Balikpapan, Indonesia", network_type='drive')
        
        self.G = ox.add_edge_speeds(self.G)
        self.G = ox.add_edge_travel_times(self.G)
        
        self.G = ox.truncate.largest_component(self.G, strongly=True)
        print(f"Peta Siap! {len(self.G.nodes)} titik jalan termuat.")

    def apply_flood_data(self, flood_points):
        """
        Menghapus node (titik jalan) yang berada dalam radius banjir.
        Mendukung format data baru (latitude/longitude) dan lama (lat/lon).
        """
        print(f"Memproses pemblokiran jalan untuk {len(flood_points)} titik banjir...")
        
        nodes_to_remove = []
        removed_count = 0
        
        METERS_PER_DEGREE = 111320 

        for node, data in self.G.nodes(data=True):
            n_lat = data['y']
            n_lon = data['x']
            
            for flood in flood_points:
                f_lat = flood.get('latitude')
                if f_lat is None: f_lat = flood.get('lat')
                
                f_lon = flood.get('longitude')
                if f_lon is None: f_lon = flood.get('lon')
                
                if f_lat is None or f_lon is None:
                    continue

                radius = flood.get('radius', 150)

               
                dy = (n_lat - f_lat) * METERS_PER_DEGREE
                dx = (n_lon - f_lon) * METERS_PER_DEGREE
                
                dist_meters = (dx**2 + dy**2) ** 0.5
                
                if dist_meters <= radius:
                    nodes_to_remove.append(node)
                    break 

        for node in nodes_to_remove:
            if self.G.has_node(node):
                self.G.remove_node(node)
                removed_count += 1
                
        print(f"Berhasil memblokir {removed_count} titik jalan yang terendam banjir.")
