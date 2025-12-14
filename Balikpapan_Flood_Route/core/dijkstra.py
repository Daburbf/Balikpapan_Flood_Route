import networkx as nx
import osmnx as ox

# PERHATIKAN: Huruf 'D' Besar
class Dijkstra:
    def __init__(self, graph_manager):
        self.graph_manager = graph_manager

    def find_route(self, start_lat, start_lon, end_lat, end_lon):
        # Ambil graph dari manager
        G = self.graph_manager.G 
        
        try:
            # 1. Cari Node Terdekat (Start & End)
            orig_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
            dest_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
            
            # 2. Algoritma Dijkstra
            route_nodes = nx.shortest_path(G, orig_node, dest_node, weight='travel_time')
            
            # 3. Ambil koordinat
            route_coords = []
            for node in route_nodes:
                point = G.nodes[node]
                route_coords.append([point['y'], point['x']])
                
            return route_coords

        except Exception as e:
            print(f"Error Dijkstra: {e}")
            return None