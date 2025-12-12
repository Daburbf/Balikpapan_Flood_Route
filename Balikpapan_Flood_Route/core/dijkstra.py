import heapq
import copy

class Dijkstra:
    def __init__(self, graph):
        self.graph = graph
        self.flood_penalty = 10000

    def find_best_routes(self, start_node, end_node, max_routes=3):
        routes = []
        
        safest_route = self.find_route(start_node, end_node, avoid_floods=True)
        if safest_route:
            safest_route['type'] = 'teraman'
            safest_route['description'] = 'Rute paling aman (hindari semua banjir)'
            routes.append(safest_route)
        
        fastest_route = self.find_route(start_node, end_node, avoid_floods=False)
        if fastest_route and fastest_route != safest_route:
            fastest_route['type'] = 'tercepat'
            fastest_route['description'] = 'Rute tercepat (mungkin melewati banjir)'
            routes.append(fastest_route)
        
        for i in range(1, max_routes):
            alt_route = self.find_alternative_route(start_node, end_node, routes)
            if alt_route:
                alt_route['type'] = f'alternatif_{i}'
                alt_route['description'] = f'Rute alternatif {i}'
                routes.append(alt_route)
            
            if len(routes) >= max_routes:
                break
        
        return routes[:max_routes]

    def find_route(self, start_node, end_node, avoid_floods=True):
        distances = {node: float('inf') for node in self.graph.nodes}
        distances[start_node] = 0
        previous_nodes = {node: None for node in self.graph.nodes}
        
        priority_queue = [(0, start_node)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            if current_distance > distances[current_node]:
                continue
            
            if current_node == end_node:
                break
            
            for neighbor, weight in self.graph.get_neighbors(current_node).items():
                total_weight = weight
                if avoid_floods:
                    if self.graph.has_flood_between(current_node, neighbor):
                        total_weight += self.flood_penalty
                
                new_distance = current_distance + total_weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        path = []
        current = end_node
        
        if previous_nodes[current] is None and current != start_node:
            return None
        
        while current is not None:
            path.append(current)
            current = previous_nodes[current]
        
        path.reverse()
        
        has_flood = False
        for i in range(len(path) - 1):
            if self.graph.has_flood_between(path[i], path[i + 1]):
                has_flood = True
                break
        
        return {
            'path': path,
            'distance': distances[end_node],
            'has_flood': has_flood
        }

    def find_alternative_route(self, start_node, end_node, existing_routes):
        if not existing_routes:
            return self.find_route(start_node, end_node, avoid_floods=False)
        
        temp_graph = copy.deepcopy(self.graph)
        
        for route in existing_routes[:2]:
            path = route['path']
            for i in range(len(path) - 1):
                node1, node2 = path[i], path[i + 1]
                if node2 in temp_graph.edges.get(node1, {}):
                    temp_graph.edges[node1].pop(node2, None)
                if node1 in temp_graph.edges.get(node2, {}):
                    temp_graph.edges[node2].pop(node1, None)
        
        temp_dijkstra = Dijkstra(temp_graph)
        return temp_dijkstra.find_route(start_node, end_node, avoid_floods=False)

    def find_safe_route(self, start_node, end_node):
        return self.find_route(start_node, end_node, avoid_floods=True)

    def find_alternative_routes(self, start_node, end_node, num_routes=3):
        return self.find_best_routes(start_node, end_node, max_routes=num_routes)