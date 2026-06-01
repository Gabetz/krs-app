# 🎓 Aplikasi Web KRS Online — FastAPI & SQLAlchemy

Sistem manajemen pemilihan kelas kuliah (KRS Online) berbasis Python Web.

## ⚙️ Fitur Utama

1. **Autentikasi Multi-User** — Registrasi & Login Dosen (Admin) & Mahasiswa (User)
2. **Manajemen Kelas (CRUD Dosen)** — Dosen menambah/edit/hapus jadwal kuliah & kuota
3. **Sistem Pemilihan KRS** — Mahasiswa memilih beberapa kelas sekaligus ke daftar rencana studi, lalu submit massal untuk mengunci kuota kursi kelas secara real-time

## 🗂️ Struktur File

```
krs-app/
├── main.py              ← Entry point FastAPI
├── database.py          ← Koneksi MySQL via SQLAlchemy
├── seed.py              ← Data demo (jalankan sekali)
├── requirements.txt
├── models/
│   └── models.py        ← User, Kelas, KRS (tabel pivot)
├── routes/
│   ├── auth.py          ← Login, register, logout
│   ├── dashboard.py     ← Dashboard mahasiswa + pilih kelas
│   └── admin.py         ← CRUD kelas, mahasiswa (dosen)
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── user_dashboard.html   ← KRS mahasiswa
│   ├── kelas_list.html       ← Pilih kelas
│   ├── admin_dashboard.html
│   ├── admin_kelas.html      ← CRUD kelas
│   ├── admin_peserta.html    ← Peserta per kelas
│   └── admin_mahasiswa.html
└── static/
    ├── css/style.css
    └── js/main.js
```