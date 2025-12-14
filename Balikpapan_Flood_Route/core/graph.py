import osmnx as ox
import networkx as nx

class Graph:
    def __init__(self):
        # Download peta area Balikpapan
        # Menggunakan network_type='drive' agar fokus ke jalan raya mobil/motor
        print("Memuat Peta Balikpapan... (Harap Tunggu)")
        self.G = ox.graph_from_place("Balikpapan, Indonesia", network_type='drive')
        
        # Tambahkan kecepatan rata-rata & waktu tempuh (weight) ke setiap jalan
        self.G = ox.add_edge_speeds(self.G)
        self.G = ox.add_edge_travel_times(self.G)
        
        # Urutkan index agar pencarian lebih cepat
        self.G = ox.truncate.largest_component(self.G, strongly=True)
        print(f"Peta Siap! {len(self.G.nodes)} titik jalan termuat.")

    def apply_flood_data(self, flood_points):
        """
        Menghapus node (titik jalan) yang berada dalam radius banjir.
        Mendukung format data baru (latitude/longitude) dan lama (lat/lon).
        """
        print(f"⚡ Memproses pemblokiran jalan untuk {len(flood_points)} titik banjir...")
        
        nodes_to_remove = []
        removed_count = 0
        
        # Konstanta konversi derajat ke meter (kira-kira di ekuator/Balikpapan)
        METERS_PER_DEGREE = 111320 

        for node, data in self.G.nodes(data=True):
            # Ambil koordinat titik jalan (node)
            n_lat = data['y']
            n_lon = data['x']
            
            for flood in flood_points:
                # 1. Deteksi kunci koordinat (agar support berbagai format JSON)
                f_lat = flood.get('latitude')
                if f_lat is None: f_lat = flood.get('lat')
                
                f_lon = flood.get('longitude')
                if f_lon is None: f_lon = flood.get('lon')
                
                # Jika data koordinat tidak lengkap, lewati
                if f_lat is None or f_lon is None:
                    continue

                # Ambil radius (default 150 meter jika tidak ada)
                radius = flood.get('radius', 150)

                # 2. Hitung Jarak (Euclidean Distance Sederhana)
                # Kita ubah selisih derajat menjadi meter
                dy = (n_lat - f_lat) * METERS_PER_DEGREE
                dx = (n_lon - f_lon) * METERS_PER_DEGREE
                
                # Jarak dalam meter
                dist_meters = (dx**2 + dy**2) ** 0.5
                
                # 3. Jika masuk radius, tandai untuk dihapus
                if dist_meters <= radius:
                    nodes_to_remove.append(node)
                    break # Pindah ke node berikutnya jika sudah kena satu banjir

        # 4. Eksekusi Penghapusan
        for node in nodes_to_remove:
            if self.G.has_node(node):
                self.G.remove_node(node)
                removed_count += 1
                
        print(f"🚫 Berhasil memblokir {removed_count} titik jalan yang terendam banjir.")