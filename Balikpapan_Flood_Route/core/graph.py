import math

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.flood_edges = set()
        
    def add_node(self, node_id, coordinates):
        self.nodes[node_id] = coordinates
        if node_id not in self.edges:
            self.edges[node_id] = {}
            
    def add_edge(self, node1, node2):
        if node1 in self.nodes and node2 in self.nodes:
            distance = self.calculate_distance(node1, node2)
            self.edges.setdefault(node1, {})[node2] = distance
            self.edges.setdefault(node2, {})[node1] = distance
            
    def calculate_distance(self, node1, node2):
        coords1 = self.nodes[node1]
        coords2 = self.nodes[node2]
        
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
        
    def get_neighbors(self, node):
        return self.edges.get(node, {})
        
    def get_edge_weight(self, node1, node2):
        if node1 in self.edges and node2 in self.edges[node1]:
            return self.edges[node1][node2]
        return None
        
    def get_coordinates(self, node_id):
        return self.nodes.get(node_id)
        
    def set_flood_points(self, flood_data):
        self.flood_edges.clear()
        
        for flood in flood_data:
            if 'latitude' in flood and 'longitude' in flood:
                flood_coords = (flood['latitude'], flood['longitude'])
                
                for node1 in self.nodes:
                    for node2 in self.nodes:
                        if node1 != node2 and node2 in self.edges.get(node1, {}):
                            coords1 = self.nodes[node1]
                            coords2 = self.nodes[node2]
                            
                            if self.is_point_near_line(flood_coords, coords1, coords2):
                                self.flood_edges.add((node1, node2))
                                self.flood_edges.add((node2, node1))
                                
    def is_point_near_line(self, point, line_start, line_end, threshold=0.0003):
        lat, lon = point
        lat1, lon1 = line_start
        lat2, lon2 = line_end
        
        line_length_squared = (lat2 - lat1)**2 + (lon2 - lon1)**2
        if line_length_squared == 0:
            return math.sqrt((lat - lat1)**2 + (lon - lon1)**2) <= threshold
            
        t = max(0, min(1, ((lat - lat1) * (lat2 - lat1) + (lon - lon1) * (lon2 - lon1)) / line_length_squared))
        
        closest_lat = lat1 + t * (lat2 - lat1)
        closest_lon = lon1 + t * (lon2 - lon1)
        
        distance = math.sqrt((lat - closest_lat)**2 + (lon - closest_lon)**2)
        return distance <= threshold
        
    def has_flood_between(self, node1, node2):
        return (node1, node2) in self.flood_edges or (node2, node1) in self.flood_edges
        
    def has_flood_on_path(self, path):
        for i in range(len(path) - 1):
            if self.has_flood_between(path[i], path[i + 1]):
                return True
        return False