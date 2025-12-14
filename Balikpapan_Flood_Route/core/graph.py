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

    def apply_flood_data(self, flood_data):
        """
        Memblokir jalan yang terkena banjir dengan memberikan bobot (weight)
        yang sangat besar (Infinity).
        """
        count_blocked = 0
        for point in flood_data:
            lat = point['latitude']
            lon = point['longitude']
            # Default radius dibesarkan sedikit jika di JSON tidak ada
            radius = point.get('radius', 100) 

            # CARA BARU: Cari Node (Titik Simpang) yang masuk dalam radius banjir
            # Kita cari titik terdekat, lalu cek tetangganya juga
            center_node = ox.distance.nearest_nodes(self.G, X=lon, Y=lat)
            
            # Ambil semua jalan yang terhubung ke titik pusat banjir ini
            # Radius pencarian manual: Kita blokir titik pusat DAN tetangganya
            nodes_to_block = [center_node]
            
            # Cek tetangga (agar pemblokiran lebih luas/agresif)
            neighbors = list(self.G.neighbors(center_node))
            nodes_to_block.extend(neighbors)

            for node in nodes_to_block:
                # Blokir jalan KELUAR dari titik ini
                for u, v, key, data in self.G.edges(node, keys=True, data=True):
                    self.G[u][v][key]['travel_time'] = 99999999 
                    count_blocked += 1
                
                # Blokir jalan MASUK ke titik ini (PENTING: Biar tidak diterobos dari arah lawan)
                for u, v, key, data in self.G.in_edges(node, keys=True, data=True):
                    self.G[u][v][key]['travel_time'] = 99999999
                    count_blocked += 1

        print(f"⛔ {count_blocked} jalur jalan telah ditutup karena banjir.")