import urllib.request
import urllib.error
import time
import json
import random
import os
import sys


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app
from models import db, Artefak, Lokasi

URL = "http://localhost:5000/api/rfid_scan"

def send_rfid_data(id_artefak, id_lokasi, status="Terdeteksi RFID"):
    payload = {
        "id_artefak": id_artefak,
        "id_lokasi": id_lokasi,
        "status": status
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"status": "error", "message": str(e)}

def simulate():
    print("=== SOFTWARE EMULATOR: SENSOR RFID (VIRTUAL HARDWARE) ===")
    print("[i] Mengambil data koleksi nyata dari database...")
    
    with app.app_context():
        all_artefak = Artefak.query.all()
        all_lokasi = Lokasi.query.all()
        
        if not all_artefak or not all_lokasi:
            print("[!] Database kosong. Lakukan seeding data terlebih dahulu!")
            return

        print(f"[i] Berhasil memuat {len(all_artefak)} artefak.")
        print("[i] Menghubungkan ke server sistem di http://localhost:5000...")
        time.sleep(1)

        print("\n[Mulai Simulasi] Menunggu sensor mendeteksi kartu...")
        
        try:
            for i in range(5):
                art = random.choice(all_artefak)
                lok = random.choice(all_lokasi)
                
                print(f"\n[SCAN] BIP! Chip terdeteksi: {art.nama_artefak}")
                print(f"[DATA] Mengirim data ke lokasi: {lok.nama_lokasi}")
                
                res = send_rfid_data(art.id_artefak, lok.id_lokasi, "Pengecekan Rutin (Simulasi)")
                
                if res.get("status") == "success":
                    print(f"[SERVER] Respon OK: {res.get('message')}")
                else:
                    print(f"[SERVER] Respon Error: {res.get('message')}")
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n[Selesai] Emulator dimatikan.")

if __name__ == "__main__":
    simulate()
