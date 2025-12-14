import sys
import subprocess
import os

print("="*50)
print(" DIAGNOSA PYTHON VS CODE ")
print("="*50)

# 1. Cek Python mana yang sedang dipakai tombol Play
python_path = sys.executable
print(f"🔍 Tombol Play menggunakan Python di:\n   {python_path}")

# 2. Paksa install library ke Python TERSEBUT
print("\n🛠️  Sedang menginstall library ke Python ini...")
libraries = ['osmnx', 'networkx', 'scikit-learn', 'requests', 'folium', 'PyQtWebEngine', 'PyQt5']

try:
    # Perintah ini memaksa pip berjalan di python yang sama dengan yang sedang run
    subprocess.check_call([python_path, "-m", "pip", "install"] + libraries)
    print("\n✅ SUKSES! Semua library berhasil diinstall di Python ini.")
    print("👉 Sekarang Anda bisa kembali ke 'main.py' dan tekan tombol Play.")
except Exception as e:
    print(f"\n❌ Gagal install: {e}")

print("="*50)
input("Tekan Enter untuk keluar...")