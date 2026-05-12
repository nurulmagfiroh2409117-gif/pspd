from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from datetime import datetime, date
from models import db, User, Artefak, Lokasi, Pergerakan, Laporan, LogAktivitas

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "rahasia_app"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database_galeri.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
   
    if not User.query.filter_by(username="admin").first():
        admin = User(
            nama="Administrator",
            username="admin",
            password="admin",  
            role="Admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin/admin")
    

    if not Lokasi.query.first():
        lokasi_list = [
            Lokasi(nama_lokasi="Galeri 1", jenis_lokasi="Ruang Pameran"),
            Lokasi(nama_lokasi="Galeri 2", jenis_lokasi="Ruang Pameran"),
            Lokasi(nama_lokasi="Gudang Utama", jenis_lokasi="Penyimpanan"),
            Lokasi(nama_lokasi="Laboratorium Konservasi", jenis_lokasi="Pemeliharaan")
        ]
        db.session.add_all(lokasi_list)
        db.session.commit()
        print("Sample locations created")

   
    if not Artefak.query.first():
        artefak_list = [
            Artefak(nama_artefak="Patung Merlion Kuno", kategori="Patung", tahun="1920", status="Tersedia"),
            Artefak(nama_artefak="Lukisan Pemandangan Temasek", kategori="Lukisan", tahun="1850", status="Tersedia")
        ]
        db.session.add_all(artefak_list)
        db.session.commit()
        print("Sample artifacts created")


def catat_log(aksi, tabel, id_data, keterangan, user_id=None):
    if user_id is None:
        user_id = session.get("user_id", None)
    try:
        log = LogAktivitas(id_user=user_id, aksi=aksi, tabel=tabel, id_data=id_data, keterangan=keterangan)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Log error:", e)


@app.route("/api/rfid_scan", methods=["POST"])
def api_rfid_scan():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    try:
        id_art = data.get('id_artefak')
        id_lok = data.get('id_lokasi')
        
        baru = Pergerakan(
            id_artefak=id_art,
            id_lokasi=id_lok,
            id_user=None, 
            status=data.get('status', 'Terdeteksi RFID'),
            sumber_data="RFID Sensor"
        )
        db.session.add(baru)
        db.session.commit()
        
        catat_log("RFID_SCAN", "pergerakan", baru.id_pergerakan, f"Otomatis: Artefak {id_art} terpantau di Lokasi {id_lok}")
        
        return jsonify({"status": "success", "message": "Data tercatat"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def index():
    t_art = Artefak.query.count()
    t_perg = Pergerakan.query.count()
    t_lap = Laporan.query.count()
    return render_template("index.html", t_art=t_art, t_perg=t_perg, t_lap=t_lap)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session["user_id"] = user.id_user
        session["username"] = user.username
        session["nama"] = user.nama
        session["role"] = user.role
        catat_log("Login", "user", user.id_user, "User login")
        flash("Selamat datang kembali!", "success")
    else:
        flash("Username atau password salah!", "danger")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    uid = session.get("user_id")
    if uid:
        catat_log("Logout", "user", uid, "User logout")
    session.clear()
    return redirect(url_for("index"))

@app.route("/koleksi")
def show_koleksi():
    data = Artefak.query.all()
    laporan_all = Laporan.query.order_by(Laporan.tanggal.desc()).all()
    return render_template("koleksi.html", artefak=data, laporan=laporan_all)

@app.route("/artefak/tambah", methods=["GET", "POST"])
def tambah_artefak():
    if "user_id" not in session: return redirect(url_for("index"))
    if request.method == "POST":
        baru = Artefak(
            nama_artefak=request.form.get("nama_artefak"),
            kategori=request.form.get("kategori"),
            tahun=request.form.get("tahun"),
            status=request.form.get("status")
        )
        db.session.add(baru)
        db.session.commit()
        catat_log("Tambah", "artefak", baru.id_artefak, f"Menambah artefak: {baru.nama_artefak}")
        flash("Artefak berhasil ditambahkan.", "success")
        return redirect(url_for("show_koleksi"))
    return render_template("tambah_artefak.html")

@app.route("/artefak/edit/<int:id>", methods=["GET", "POST"])
def edit_artefak(id):
    if "user_id" not in session: return redirect(url_for("index"))
    artefak = Artefak.query.get_or_404(id)
    if request.method == "POST":
        artefak.nama_artefak = request.form.get("nama_artefak")
        artefak.kategori = request.form.get("kategori")
        artefak.tahun = request.form.get("tahun")
        artefak.status = request.form.get("status")
        db.session.commit()
        catat_log("Edit", "artefak", id, f"Mengubah data artefak: {artefak.nama_artefak}")
        flash("Data artefak berhasil diperbarui.", "success")
        return redirect(url_for("show_koleksi"))
    return render_template("edit_artefak.html", artefak=artefak)

@app.route("/detail/<int:id>")
def detail_artefak(id):
    artefak = Artefak.query.get_or_404(id)
    riwayat_pergerakan = Pergerakan.query.filter_by(id_artefak=id).order_by(Pergerakan.tanggal.desc()).all()
    riwayat_laporan = Laporan.query.filter_by(id_artefak=id).order_by(Laporan.tanggal.desc()).all()
    return render_template("detail.html", artefak=artefak, pergerakan=riwayat_pergerakan, laporan=riwayat_laporan)

@app.route("/artefak/hapus/<int:id>", methods=["POST"])
def hapus_artefak(id):
    if "user_id" not in session: return redirect(url_for("index"))
    artefak = Artefak.query.get(id)
    if artefak:
        Pergerakan.query.filter_by(id_artefak=id).delete()
        Laporan.query.filter_by(id_artefak=id).delete()
        db.session.delete(artefak)
        db.session.commit()
        catat_log("Hapus", "artefak", id, f"Menghapus artefak ID {id}")
        flash("Artefak berhasil dihapus.", "success")
    return redirect(url_for("show_koleksi"))

@app.route("/pergerakan")
def show_pergerakan():
    data = Pergerakan.query.order_by(Pergerakan.tanggal.desc()).all()
    return render_template("pergerakan.html", pergerakan=data)

@app.route("/pergerakan/tambah", methods=["GET", "POST"])
def tambah_pergerakan():
    if "user_id" not in session: return redirect(url_for("index"))
    if request.method == "POST":
        baru = Pergerakan(
            id_artefak=request.form.get("id_artefak"),
            id_lokasi=request.form.get("id_lokasi"),
            id_user=session["user_id"],
            status=request.form.get("status"),
            sumber_data="Manual"
        )
        db.session.add(baru)
        db.session.commit()
        catat_log("Tambah", "pergerakan", baru.id_pergerakan, f"Mencatat pergerakan manual")
        flash("Pergerakan berhasil dicatat.", "success")
        return redirect(url_for("show_pergerakan"))
    artefak = Artefak.query.all()
    lokasi = Lokasi.query.all()
    return render_template("tambah_pergerakan.html", artefak=artefak, lokasi=lokasi)
    
@app.route("/laporan/tambah", methods=["GET", "POST"])
def tambah_laporan():
    if "user_id" not in session: return redirect(url_for("index"))
    if request.method == "POST":
        baru = Laporan(
            id_artefak=request.form.get("id_artefak"),
            jenis_laporan=request.form.get("jenis_laporan"),
            keterangan=request.form.get("keterangan")
        )
        db.session.add(baru)
        db.session.commit()
        catat_log("Tambah", "laporan", baru.id_laporan, f"Menambah laporan untuk artefak ID {baru.id_artefak}")
        flash("Laporan berhasil ditambahkan.", "success")
        return redirect(url_for("show_koleksi"))
    artefak = Artefak.query.all()
    return render_template("tambah_laporan.html", artefak=artefak)

@app.route("/laporan/edit/<int:id>", methods=["GET", "POST"])
def edit_laporan(id):
    if "user_id" not in session: return redirect(url_for("index"))
    laporan = Laporan.query.get_or_404(id)
    if request.method == "POST":
        laporan.jenis_laporan = request.form.get("jenis_laporan")
        laporan.keterangan = request.form.get("keterangan")
        db.session.commit()
        catat_log("Edit", "laporan", id, f"Mengubah laporan ID {id}")
        flash("Laporan berhasil diperbarui.", "success")
        return redirect(url_for("show_koleksi"))
    return render_template("edit_laporan.html", laporan=laporan)

@app.route("/laporan/hapus/<int:id>", methods=["POST"])
def hapus_laporan(id):
    if "user_id" not in session: return redirect(url_for("index"))
    laporan = Laporan.query.get(id)
    if laporan:
        db.session.delete(laporan)
        db.session.commit()
        catat_log("Hapus", "laporan", id, f"Menghapus laporan ID {id}")
        flash("Laporan berhasil dihapus.", "success")
    return redirect(url_for("show_koleksi"))

@app.route("/log")
def show_log():
    if "user_id" not in session: return redirect(url_for("index"))
    logs = LogAktivitas.query.order_by(LogAktivitas.waktu.desc()).all()
    return render_template("log.html", logs=logs)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)