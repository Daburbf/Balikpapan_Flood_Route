import osmnx as ox
import networkx as nx

class Graph:
    def __init__(self):
        print("Memuat Peta Balikpapan... (Harap Tunggu)")
        # Download jalan raya (drive) untuk area Balikpapan
        # Ini akan otomatis membuat ribuan nodes sesuai jalan aspal
        self.G = ox.graph_from_place('Balikpapan, Indonesia', network_type='drive')
        
        # Tambahkan estimasi waktu tempuh ke setiap jalan
        self.G = ox.add_edge_speeds(self.G)
        self.G = ox.add_edge_travel_times(self.G)
        
        # Simpan versi "Bersih" (Tanpa banjir) untuk reset
        self.base_G = self.G.copy()
        print(f"Peta Siap! {len(self.G.nodes)} titik jalan termuat.")

    def get_nearest_node(self, lat, lon):
        """Mencari titik jalan terdekat dari koordinat klik user"""
        return ox.distance.nearest_nodes(self.G, X=lon, Y=lat)

    def apply_flood_data(self, flood_data):
        """
        INTI AI: Memanipulasi bobot graph berdasarkan data banjir.
        """
        # Reset graph ke kondisi bersih dulu
        self.G = self.base_G.copy()
        
        count = 0
        for flood in flood_data:
            lat = flood['latitude']
            lon = flood['longitude']
            radius = flood['radius']
            
            # Cari titik pusat banjir di jalan
            center_node = ox.distance.nearest_nodes(self.G, X=lon, Y=lat)
            
            # Cari semua node jalan dalam radius banjir
            affected_nodes = nx.single_source_dijkstra_path_length(
                self.G, center_node, cutoff=radius, weight='length'
            )
            
            # HUKUMAN: Buat jalan yang kena banjir jadi SANGAT LAMBAT
            for node in affected_nodes:
                # Ambil semua jalan yang keluar dari node ini
                for u, v, key, data in self.G.edges(node, keys=True, data=True):
                    # Ubah bobot 'travel_time' jadi Infinity (9999999 detik)
                    # Sehingga algoritma Dijkstra akan menghindarinya
                    self.G[u][v][key]['travel_time'] = 99999999 
                    count += 1
                    
        print(f"Data banjir diaplikasikan. {count} ruas jalan ditutup.")