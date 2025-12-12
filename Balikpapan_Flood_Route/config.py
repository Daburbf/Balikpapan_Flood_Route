import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
    
    DATABASE_FILE = os.path.join(DATA_DIR, 'database.json')
    FLOOD_DATA_FILE = os.path.join(DATA_DIR, 'flood_data.json')
    STREET_DATA_FILE = os.path.join(DATA_DIR, 'street_data.json')
    
    MAP_CENTER = [-1.2680, 116.8288]
    MAP_ZOOM = 13
    MAP_TILES = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    
    FLOOD_WEIGHT_MULTIPLIER = 10
    NORMAL_ROAD_WEIGHT = 1
    
    WINDOW_TITLE = "Balikpapan Flood Route Planner"
    WINDOW_SIZE = (1200, 800)
    THEME_FILE = os.path.join(ASSETS_DIR, 'styles', 'dark_theme.qss')