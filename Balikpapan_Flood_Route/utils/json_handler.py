import json
import os
from config import Config

class JSONHandler:
    @staticmethod
    def load_data(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File {file_path} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}")
            return {}

    @staticmethod
    def save_data(file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def get_flood_data():
        return JSONHandler.load_data(Config.FLOOD_DATA_FILE)

    @staticmethod
    def get_street_data():
        return JSONHandler.load_data(Config.STREET_DATA_FILE)

    @staticmethod
    def update_flood_data(new_flood_points):
        current_data = JSONHandler.get_flood_data()
        current_data['flood_points'].extend(new_flood_points)
        JSONHandler.save_data(Config.FLOOD_DATA_FILE, current_data)