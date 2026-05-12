from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50))
    
    
    pergerakan_riwayat = db.relationship('Pergerakan', backref='user_pencatat', lazy=True)
    log_aktivitas = db.relationship('LogAktivitas', backref='user_pelaku', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

class Artefak(db.Model):
    __tablename__ = 'artefak'
    id_artefak = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_artefak = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    tahun = db.Column(db.String(10)) 
    status = db.Column(db.String(50))

    def __init__(self, **kwargs):
        super(Artefak, self).__init__(**kwargs)

class Lokasi(db.Model):
    __tablename__ = 'lokasi'
    id_lokasi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_lokasi = db.Column(db.String(100), nullable=False)
    jenis_lokasi = db.Column(db.String(50)) 

    def __init__(self, **kwargs):
        super(Lokasi, self).__init__(**kwargs)

class Pergerakan(db.Model):
    __tablename__ = 'pergerakan'
    id_pergerakan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_artefak = db.Column(db.Integer, db.ForeignKey('artefak.id_artefak'), nullable=False)
    id_lokasi = db.Column(db.Integer, db.ForeignKey('lokasi.id_lokasi'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=True)
    tanggal = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(50))
    sumber_data = db.Column(db.String(50))

    # Definisi relationship yang bersih (menggunakan backref tunggal yang konsisten)
    artefak_item = db.relationship('Artefak', backref=db.backref('riwayat_pergerakan', lazy=True))
    lokasi_sasaran = db.relationship('Lokasi', backref=db.backref('riwayat_pergerakan', lazy=True))

    def __init__(self, **kwargs):
        super(Pergerakan, self).__init__(**kwargs)

class Laporan(db.Model):
    __tablename__ = 'laporan'
    id_laporan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_artefak = db.Column(db.Integer, db.ForeignKey('artefak.id_artefak'), nullable=False)
    jenis_laporan = db.Column(db.String(50)) 
    tanggal = db.Column(db.Date, default=date.today)
    keterangan = db.Column(db.Text)

    artefak_item = db.relationship('Artefak', backref=db.backref('laporan_riwayat', lazy=True))

    def __init__(self, **kwargs):
        super(Laporan, self).__init__(**kwargs)

class LogAktivitas(db.Model):
    __tablename__ = 'log_aktivitas'
    id_log = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=True)
    aksi = db.Column(db.String(50)) 
    tabel = db.Column(db.String(50))
    id_data = db.Column(db.Integer)  
    waktu = db.Column(db.DateTime, default=datetime.now)
    keterangan = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(LogAktivitas, self).__init__(**kwargs)