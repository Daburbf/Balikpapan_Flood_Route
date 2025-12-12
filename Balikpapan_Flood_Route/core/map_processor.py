import json
import math

class MapProcessor:
    
    BALIKPAPAN_BOUNDS = {
        'min_lat': -1.35,
        'max_lat': -1.15,
        'min_lon': 116.70,
        'max_lon': 116.95
    }
    
    @classmethod
    def filter_balikpapan_data(cls, data_list):
        filtered = []
        for item in data_list:
            lat = item.get('latitude', 0)
            lon = item.get('longitude', 0)
            
            if (cls.BALIKPAPAN_BOUNDS['min_lat'] <= lat <= cls.BALIKPAPAN_BOUNDS['max_lat'] and
                cls.BALIKPAPAN_BOUNDS['min_lon'] <= lon <= cls.BALIKPAPAN_BOUNDS['max_lon']):
                filtered.append(item)
        
        return filtered
    
    @classmethod
    def calculate_distance(cls, coord1, coord2):
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return 6371000 * c
    
    @classmethod
    def is_in_balikpapan(cls, lat, lon):
        return (cls.BALIKPAPAN_BOUNDS['min_lat'] <= lat <= cls.BALIKPAPAN_BOUNDS['max_lat'] and
                cls.BALIKPAPAN_BOUNDS['min_lon'] <= lon <= cls.BALIKPAPAN_BOUNDS['max_lon'])