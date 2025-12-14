import heapq

class Dijkstra:
    def __init__(self, graph):
        self.graph = graph.G  # Mengambil object graph NetworkX

    def find_route(self, start_lat, start_lon, end_lat, end_lon):
        # 1. Cari Node terdekat dari koordinat input
        start_node = self.get_nearest_node(start_lat, start_lon)
        end_node = self.get_nearest_node(end_lat, end_lon)

        if not start_node or not end_node:
            return None

        # 2. Algoritma Dijkstra Standard
        queue = [(0, start_node)]
        distances = {start_node: 0}
        previous_nodes = {start_node: None}
        
        target_found = False

        while queue:
            current_dist, current_node = heapq.heappop(queue)

            if current_node == end_node:
                target_found = True
                break

            if current_dist > distances.get(current_node, float('inf')):
                continue

            for neighbor, edge_data in self.graph[current_node].items():
                # edge_data adalah dictionary, ambil item pertama (key 0 untuk multigraph)
                attributes = edge_data.get(0, {}) 
                weight = attributes.get('length', 1)
                
                distance = current_dist + weight

                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

        if not target_found:
            return None

        # 3. Rekonstruksi Jalur (Backtracking)
        path_nodes = []
        curr = end_node
        while curr is not None:
            path_nodes.append(curr)
            curr = previous_nodes[curr]
        path_nodes.reverse() # Balik urutan agar dari Start -> End

        # --- BAGIAN PENTING: MENGAMBIL GEOMETRI (LEKUKAN) ---
        route_coords = []
        
        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i+1]
            
            # Ambil data jalan antara titik U dan V
            edge_data = self.graph.get_edge_data(u, v)[0]
            
            # Cek apakah jalan ini punya data 'geometry' (lekukan detail)
            if 'geometry' in edge_data:
                # Geometry formatnya (Lon, Lat), kita butuh (Lat, Lon)
                # coords list otomatis ada jika pakai OSMnx
                geo_coords = list(edge_data['geometry'].coords)
                
                # Tukar posisi dari (Lon, Lat) ke (Lat, Lon)
                for lon, lat in geo_coords:
                    route_coords.append([lat, lon])
            else:
                # Jika tidak ada lekukan (jalan lurus), ambil titik ujungnya saja
                node_data = self.graph.nodes[u]
                route_coords.append([node_data['y'], node_data['x']])
        
        # Tambahkan titik terakhir
        last_node = self.graph.nodes[path_nodes[-1]]
        route_coords.append([last_node['y'], last_node['x']])

        return route_coords

    def get_nearest_node(self, lat, lon):
        """Mencari node graph terdekat dari koordinat user (Euclidean distance)"""
        nearest_node = None
        min_dist = float('inf')
        
        for node, data in self.graph.nodes(data=True):
            dist = (data['y'] - lat)**2 + (data['x'] - lon)**2
            if dist < min_dist:
                min_dist = dist
                nearest_node = node
        return nearest_node