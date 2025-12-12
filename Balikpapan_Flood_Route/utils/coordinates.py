import math

class Coordinates:
    @staticmethod
    def calculate_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        radius = 6371
        distance = radius * c * 1000
        
        return distance

    @staticmethod
    def is_point_in_flood_area(point, flood_area, radius_meters=50):
        for flood_point in flood_area:
            distance = Coordinates.calculate_distance(point, flood_point)
            if distance <= radius_meters:
                return True
        return False