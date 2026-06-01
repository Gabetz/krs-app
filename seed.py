"""
Jalankan sekali untuk mengisi data demo:
    python seed.py
"""
from database import engine, SessionLocal, Base
from models.models import User, Kelas
from passlib.hash import bcrypt
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Hapus data lama (opsional)
db.execute(text("DELETE FROM krs"))
db.execute(text("DELETE FROM kelas"))
db.execute(text("DELETE FROM users"))
db.commit()

# ── Users ──────────────────────────────────────────────────────
users = [
    User(nama_lengkap="Dr. Ahmad Dosen", username="admin",       email="admin@kampus.ac.id",       nim_nip="NIP001", hashed_password=bcrypt.hash("admin123"),   role="dosen"),
    User(nama_lengkap="Siti Rahayu",     username="mahasiswa1",  email="siti@mhs.kampus.ac.id",    nim_nip="2024001001", hashed_password=bcrypt.hash("mhs123"), role="mahasiswa"),
    User(nama_lengkap="Budi Santoso",    username="mahasiswa2",  email="budi@mhs.kampus.ac.id",    nim_nip="2024001002", hashed_password=bcrypt.hash("mhs123"), role="mahasiswa"),
    User(nama_lengkap="Dewi Lestari",    username="mahasiswa3",  email="dewi@mhs.kampus.ac.id",    nim_nip="2024001003", hashed_password=bcrypt.hash("mhs123"), role="mahasiswa"),
]
for u in users:
    db.add(u)
db.commit()
for u in users:
    db.refresh(u)

dosen = users[0]

# ── Kelas ──────────────────────────────────────────────────────
kelas_data = [
    Kelas(kode_kelas="CS101-A", nama_matkul="Algoritma & Pemrograman",  sks=3, hari="Senin",  jam_mulai="07:00", jam_selesai="09:30", ruangan="Gedung A-101", kuota=30, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="CS102-A", nama_matkul="Basis Data",               sks=3, hari="Selasa", jam_mulai="09:00", jam_selesai="11:30", ruangan="Gedung A-201", kuota=25, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="CS103-A", nama_matkul="Jaringan Komputer",        sks=2, hari="Rabu",   jam_mulai="13:00", jam_selesai="14:40", ruangan="Lab Jaringan", kuota=20, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="MA101-A", nama_matkul="Kalkulus II",              sks=3, hari="Kamis",  jam_mulai="07:00", jam_selesai="09:30", ruangan="Gedung B-301", kuota=35, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="EN101-A", nama_matkul="Bahasa Inggris Teknis",    sks=2, hari="Jumat",  jam_mulai="10:00", jam_selesai="11:40", ruangan="Gedung C-101", kuota=30, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="CS104-A", nama_matkul="Pemrograman Web",          sks=3, hari="Senin",  jam_mulai="13:00", jam_selesai="15:30", ruangan="Lab Komputer", kuota=25, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="CS105-A", nama_matkul="Sistem Operasi",           sks=3, hari="Rabu",   jam_mulai="07:00", jam_selesai="09:30", ruangan="Gedung A-301", kuota=30, dosen_id=dosen.id, semester="Genap 2024/2025"),
    Kelas(kode_kelas="MA102-A", nama_matkul="Statistika & Probabilitas",sks=3, hari="Selasa", jam_mulai="13:00", jam_selesai="15:30", ruangan="Gedung B-201", kuota=30, dosen_id=dosen.id, semester="Genap 2024/2025"),
]
for k in kelas_data:
    db.add(k)
db.commit()

db.close()
print("✅ Seed selesai! Akun demo:")
print("   Dosen  : admin / admin123")
print("   Mhs 1  : mahasiswa1 / mhs123")
print("   Mhs 2  : mahasiswa2 / mhs123")
