import math

class RouteCalculator:
    def __init__(self, graph=None):
        self.graph = graph
    
    @staticmethod
    def calculate_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def estimate_travel_time(self, distance_meters, transport_type, has_flood=False):
        base_speeds = {
            'car': 40,
            'motor': 30,
            'walk': 5
        }
        
        if transport_type not in base_speeds:
            return 0
        
        base_speed = base_speeds[transport_type]
        
        if has_flood:
            if transport_type == 'car':
                base_speed *= 0.6
            elif transport_type == 'motor':
                base_speed *= 0.7
            elif transport_type == 'walk':
                base_speed *= 0.5
        
        time_hours = distance_meters / 1000 / base_speed
        time_minutes = time_hours * 60
        
        return max(1, int(round(time_minutes)))
    
    def calculate_route_time_estimates(self, path_nodes, graph, has_flood=False):
        if not path_nodes or len(path_nodes) < 2:
            return {'car': 0, 'motor': 0, 'walk': 0}
        
        total_distance = 0
        for i in range(len(path_nodes) - 1):
            node1 = path_nodes[i]
            node2 = path_nodes[i + 1]
            weight = graph.get_edge_weight(node1, node2)
            if weight:
                total_distance += weight
            else:
                coords1 = graph.get_coordinates(node1)
                coords2 = graph.get_coordinates(node2)
                total_distance += self.calculate_distance(coords1, coords2)
        
        estimates = {}
        for transport in ['car', 'motor', 'walk']:
            estimates[transport] = self.estimate_travel_time(total_distance, transport, has_flood)
        
        return estimates
    
    @staticmethod
    def format_distance(distance_meters):
        if distance_meters < 1000:
            return f"{distance_meters:.0f} m"
        else:
            return f"{distance_meters/1000:.1f} km"
    
    @staticmethod
    def format_time(minutes):
        if minutes < 60:
            return f"{minutes} min"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours} jam {mins} min"