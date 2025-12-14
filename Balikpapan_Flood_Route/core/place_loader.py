import csv
import os

def load_places_from_csv(filename="tempat_balikpapan.csv"):
    """
    Membaca file CSV dan mengubahnya menjadi Dictionary.
    Format: {"Nama Tempat": (Latitude, Longitude)}
    """
    places_dict = {}
    
    # Cek apakah file ada
    if not os.path.exists(filename):
        print(f"⚠️ File {filename} tidak ditemukan. Menggunakan data kosong.")
        return places_dict

    try:
        with open(filename, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['nama_tempat']
                lat = float(row['lat'])
                lon = float(row['lon'])
                category = row['kategori']
                
                # Kita gabungkan nama + kategori agar lebih jelas
                # Contoh: "ATM BNI (ATM)"
                full_name = f"{name} ({category})"
                
                # Simpan ke dictionary
                places_dict[full_name] = (lat, lon)
                
        print(f"✅ Berhasil memuat {len(places_dict)} tempat dari CSV.")
    except Exception as e:
        print(f"❌ Gagal membaca CSV: {e}")
        
    return places_dict