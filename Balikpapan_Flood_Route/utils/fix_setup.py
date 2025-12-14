import sys
import subprocess
import os

print("="*50)
print(" DIAGNOSA PYTHON VS CODE ")
print("="*50)

python_path = sys.executable
print(f"Tombol Play menggunakan Python di:\n   {python_path}")

print("\nSedang menginstall library ke Python ini...")
libraries = ['osmnx', 'networkx', 'scikit-learn', 'requests', 'folium', 'PyQtWebEngine', 'PyQt5']

try:

    subprocess.check_call([python_path, "-m", "pip", "install"] + libraries)
    print("\nSUKSES! Semua library berhasil diinstall di Python ini.")
    print("Sekarang Anda bisa kembali ke 'main.py' dan tekan tombol Play.")
except Exception as e:
    print(f"\nGagal install: {e}")

print("="*50)
input("Tekan Enter untuk keluar...")
