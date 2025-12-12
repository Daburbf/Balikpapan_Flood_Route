import os
import json
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file="data/search_history.json"):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_route_search(self, start_location, end_location, route_data):
        history_item = {
            'id': len(self.history) + 1,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'start': start_location,
            'end': end_location,
            'route': route_data
        }
        self.history.insert(0, history_item)
        if len(self.history) > 100:
            self.history = self.history[:100]
        self.save_history()
    
    def get_recent_history(self, limit=20):
        return self.history[:limit]
    
    def clear_history(self):
        self.history = []
        self.save_history()