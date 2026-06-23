# 🎯 Sistem Manajemen Risiko KPPN

Sistem manajemen risiko online terpusat untuk KPPN yang mengumpulkan, menganalisis, dan memantau risiko operasional dari lima seksi berbeda.

> **Catatan dokumen ini**: README ini disusun ulang berdasarkan pemeriksaan langsung terhadap kode backend dan frontend yang berjalan saat ini, bukan rancangan awal proyek. Bagian yang ditandai ⚠️ menunjukkan gap antara rancangan awal dan implementasi nyata yang masih perlu dikerjakan.

## ✨ Fitur Utama (Sudah Berfungsi)

- ✅ **Multi-User Multi-Section**: Seksi MSKI, Seksi Bank, Seksi PD, Seksi Vera, Subbagian Umum
- ✅ **25 Indikator Risiko Aktif**: IKU, Non-IKU, Mandatory (termasuk 4 Indikator Bersama dengan dua PIC)
- ✅ **Kalkulasi Risiko Resmi**: Frekuensi (1-5) × Dampak (1-5), dipetakan ke kategori warna sesuai **Matriks Resmi Kementerian Keuangan (Pola 5x5)** — bukan perkalian sederhana
- ✅ **Matriks Risiko Visual**: 5 kategori warna (Biru, Hijau, Kuning, Jingga, Merah)
- ✅ **Quarter-Based Locking**: Form input hanya aktif sesuai jadwal kuartal kalender (lihat tabel di bawah); Admin dapat bypass jika diperlukan
- ✅ **Batch Submit**: Kirim Final sekaligus untuk seluruh 25 indikator per quarter, bukan satu per satu
- ✅ **Dashboard Auto-Refresh**: Ringkasan kategori risiko memuat ulang otomatis setiap 30 detik
- ✅ **Upload Dokumen Pendukung**: Validasi tipe file berdasarkan isi file (magic bytes), maksimal 25 MB
- ✅ **Reset Password oleh Admin**: Tanpa email — Admin men-generate password sementara, user dipaksa ganti password saat login pertama
- ✅ **Draft Lokal Otomatis**: Data form tersimpan sementara di browser saat koneksi terputus
- ✅ **Audit Logging**: Aksi login, register, reset password, dan ganti password tercatat otomatis
- ✅ **JWT Authentication**: Access token (1 jam) + Refresh token (7 hari), dengan mekanisme logout/blacklist
- ✅ **Role-Based Access Control**: User hanya dapat mengakses data seksinya sendiri; Indikator Bersama dapat dilihat (read-only) oleh PIC Pendamping

## ⚠️ Fitur yang Disebut di Rancangan Awal Tapi Belum Tersedia

Bagian ini penting dibaca sebelum mengembangkan fitur baru, agar tidak mengasumsikan sesuatu sudah ada padahal belum:

- **Export PDF dan Export ZIP (bukti pendukung)** — belum ada di backend. Hanya Export CSV dan Excel yang tersedia di rancangan, dan keduanya pun **belum memiliki endpoint backend** (lihat poin selanjutnya).
- **Endpoint `GET /laporan/export`** — dipanggil oleh tombol Export CSV/Excel di frontend, namun **belum diimplementasikan** di backend. Mengklik tombol ini saat ini akan menghasilkan error 404.
- **Fitur Verifikasi/Approve/Reject data oleh Admin** — status assessment hanya mengenal `draft` dan `submitted`; tidak ada status `verified` maupun endpoint approve/reject. Blueprint `routes/admin.py` bahkan tidak terdaftar di `app.py`, sehingga seluruh path `/api/admin/*` tidak aktif.
- **Reset password mandiri via email** — sengaja tidak digunakan. Sistem ini memakai mekanisme reset oleh Admin sebagai gantinya (lihat bagian Keamanan).
- **Tampilan tracking P26 → R26 dan grafik perubahan Q1→Q2→Q3→Q4** — belum ada halaman/komponen khusus untuk ini. Data riwayat tersimpan di database dan dapat diambil lewat `GET /risiko/assessments`, namun belum divisualisasikan di frontend.
- **Halaman terpisah "Lihat Data" / "Edit Data Lama"** — saat ini dashboard hanya menampilkan ringkasan dan daftar indikator; melihat/mengedit assessment individual dilakukan lewat halaman Input Data dan endpoint API langsung, belum ada tabel data lengkap yang bisa diklik per baris di UI.

## 📋 25 Indikator Risiko

Jumlah resmi indikator aktif adalah **25**, sesuai dokumen referensi `Mitigasi_Risiko.xlsx`. 4 indikator (`2b-N-01`, `3c-N-01`, `5b-N-01`, `5c-N-01`) yang sebelumnya ada di draft data telah dinonaktifkan (`is_active = false`) karena tidak terdaftar di dokumen resmi.

### Indikator Bersama (Multi-PIC)

4 indikator berikut memiliki dua PIC — PIC Utama yang mengisi data, dan PIC Pendamping yang hanya dapat melihat (read-only):

| Kode | Indikator | PIC Utama | PIC Pendamping |
|---|---|---|---|
| RE#2.3 | Respon pertanyaan/konsultasi tidak tepat waktu | Seksi MSKI | Subbagian Umum |
| RE#3.3 | Waktu pengajuan SPM tidak sesuai RPD | Seksi PD | Seksi MSKI |
| RE#5.1 | Persepsi negatif masyarakat | Subbagian Umum | Seksi MSKI |
| RE#6.1 | Kebocoran data dan informasi | Subbagian Umum | Seksi MSKI |

## 📊 Matriks Risiko (Standar Kementerian Keuangan)

Sistem menggunakan **Matriks Analisis Risiko Organisasi — Pola 5x5** resmi dari Kementerian Keuangan RI, bukan rumus perkalian sederhana. Setiap kombinasi Frekuensi × Dampak memiliki kategori warna yang ditetapkan secara eksplisit di tabel `risk_matrix_mapping`, bukan dihitung di kode aplikasi.

```
KATEGORI:
🟦 BIRU:    Risiko Rendah
🟩 HIJAU:   Risiko Sedang Rendah
🟨 KUNING:  Risiko Sedang
🟧 JINGGA:  Risiko Tinggi
🟥 MERAH:   Risiko Sangat Tinggi
```

> Lihat `database/initial_data.sql` untuk 25 baris pemetaan resmi lengkap, atau gambar referensi "Matriks Analisis Risiko Organisasi" dari Kemenkeu sebagai sumber kebenaran.

## 👥 User & Role

| Role | Akses |
|------|-------|
| **Admin** | Melihat & input data seluruh seksi, kelola akun pengguna, reset password, bypass quarter-lock |
| **User (per Seksi)** | Input Q1–Q4 hanya untuk indikator yang menjadi PIC seksinya; dapat melihat (read-only) Indikator Bersama di mana seksinya tercatat sebagai PIC Pendamping |

Seksi yang tersedia: **Seksi MSKI, Seksi Bank, Seksi PD, Seksi Vera, Subbagian Umum**.

## 📅 Jadwal Input Data (Quarter Locking)

Sistem menggunakan jadwal kuartal kalender standar. Konstanta ini didefinisikan di `backend/config.py` (`QUARTER_EDIT_WINDOWS`) dan di-mirror di `frontend/src/utils/helpers.js`:

| Quarter | Periode Bulan | Dibuka | Dikunci Otomatis |
|---|---|---|---|
| Q1 | Januari–Maret | 1 Januari | 31 Maret, 23:59 |
| Q2 | April–Juni | 1 April | 30 Juni, 23:59 |
| Q3 | Juli–September | 1 Juli | 30 September, 23:59 |
| Q4 | Oktober–Desember | 1 Oktober | 31 Desember, 23:59 |

Admin memiliki hak akses istimewa untuk melakukan koreksi data (bypass lock) kapan saja jika diperlukan.

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.x (Python 3.11)
- **Database**: PostgreSQL 15 (Supabase, via connection pooler PgBouncer port 6543)
- **Authentication**: JWT via `flask-jwt-extended` — Access token 1 jam, Refresh token 7 hari, dengan token blacklist untuk logout
- **ORM**: SQLAlchemy (Flask-SQLAlchemy) + Flask-Migrate untuk migrasi schema
- **Server Produksi**: Gunicorn (4 worker)
- **API**: RESTful, prefix `/api`
- **Password Hashing**: Werkzeug `generate_password_hash` (PBKDF2), bukan bcrypt langsung meski `bcrypt` ada di requirements
- **File Validation**: `python-magic` untuk deteksi tipe file dari isi file (magic bytes), bukan ekstensi nama file
- **Export Spreadsheet**: `openpyxl` (tersedia di dependency, namun endpoint export belum dibangun — lihat bagian gap di atas)

### Frontend
- **Framework**: Vue.js 3 (Composition API, `<script setup>`)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Styling**: Tailwind CSS + Bootstrap 5
- **Charts**: Chart.js
- **HTTP Client**: Axios, dengan interceptor otomatis menyisipkan JWT dari `localStorage`
- **Form Validation**: VeeValidate + Yup
- **Hosting yang Direncanakan**: Netlify (frontend statis hasil `vite build`)

### Infrastructure
- **Database**: Supabase PostgreSQL (free tier, via pooler)
- **File Storage**: Disk lokal server (folder `uploads/bukti_pendukung/`) — **catatan penting**: ini tidak persisten di platform seperti Railway/Heroku/Render; file akan hilang saat redeploy. Migrasi ke object storage (Supabase Storage, dsb) diperlukan sebelum go-live produksi.
- **Containerization**: Dockerfile tersedia untuk backend, dengan `HEALTHCHECK` bawaan yang memanggil `/health`
- **Version Control**: Git + GitHub

## 📦 Struktur Project (Aktual)

```
ManRiskMSKI/
├── 📁 backend/
│   ├── app.py                      # Entry point Flask, registrasi blueprint, CORS, middleware
│   ├── config.py                   # QUARTER_EDIT_WINDOWS & fungsi is_editable()
│   ├── extensions.py                # Inisialisasi SQLAlchemy db
│   ├── models.py                    # Model: User, RiskIndicator, RiskAssessment, RiskMatrixMapping,
│   │                                 #        SupportingDocument, AuditLog, JWTBlacklist
│   ├── init_db.py                   # Script setup awal database (idempoten, aman dijalankan ulang)
│   ├── seed_data.py                 # Script contoh data dummy (perlu disesuaikan ID admin sebelum dipakai)
│   ├── fix_admin.py                 # Utilitas perbaikan akun admin
│   ├── cek_dokumen.py / test_db.py  # Script bantu debugging
│   ├── requirements.txt
│   ├── Dockerfile                   # Termasuk HEALTHCHECK ke /health
│   ├── .env                         # Variabel environment (tidak ada file .env.example terpisah)
│   ├── 📁 routes/
│   │   ├── auth.py                 # Login, register, reset password, logout, refresh, kelola user
│   │   ├── dashboard.py             # Ringkasan kategori warna per seksi/quarter
│   │   ├── risiko.py                # Indikator, assessment CRUD, batch submit, dokumen
│   │   ├── matriks.py               # Ringkasan kategori lintas seksi per quarter
│   │   ├── laporan.py               # Upload & download dokumen pendukung
│   │   └── admin.py                 # ⚠️ Placeholder kosong, TIDAK terdaftar di app.py
│   └── 📁 utils/
│       └── decorators.py            # check_section_access() dan helper otorisasi lain
│
├── 📁 frontend/
│   ├── src/
│   │   ├── 📁 components/
│   │   │   ├── MatrixVisual.vue     # Visualisasi matriks 5x5
│   │   │   ├── Navbar.vue
│   │   │   └── Sidebar.vue          # Menu navigasi, item Admin disembunyikan otomatis dari non-admin
│   │   ├── 📁 views/
│   │   │   ├── LoginPage.vue
│   │   │   ├── DashboardPage.vue    # Ringkasan + daftar 25 indikator, auto-refresh 30 detik
│   │   │   ├── InputDataPage.vue    # Form input + badge Indikator Bersama + Batch Submit
│   │   │   ├── ChangePasswordPage.vue # Wajib diakses jika must_change_password = true
│   │   │   ├── LaporanPage.vue      # Tombol Export CSV/Excel (⚠️ endpoint backend belum ada)
│   │   │   ├── AdminPage.vue        # Kelola user + Reset Password (modal sekali tampil)
│   │   │   └── RegisterPage.vue     # Tambah user baru, hanya dapat diakses Admin
│   │   ├── 📁 store/                # Pinia: auth.js, risk.js, risiko.js, matrix.js
│   │   ├── 📁 router/
│   │   │   └── index.js             # Navigation guard berdasarkan requiresAuth & requiresAdmin
│   │   ├── 📁 utils/
│   │   │   ├── api.js                # Axios instance + interceptor JWT
│   │   │   └── helpers.js            # isQuarterEditable() — mirror logic dari backend
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env                          # VITE_API_URL, VITE_APP_NAME, VITE_APP_VERSION, VITE_DEBUG
│
├── 📁 database/
│   ├── schema.sql                   # Struktur tabel (25 indikator setelah perbaikan T02)
│   └── initial_data.sql             # Data awal indikator + risk_matrix_mapping resmi 25 baris
│
└── 📁 docs/
    ├── PANDUAN_PENGGUNA.md
    ├── PANDUAN_ADMIN.md
    └── API_DOCS.md
```

> **Catatan**: folder `tests/`, file `docker-compose.yml`, dan `nginx.conf` yang disebut di rancangan awal **tidak ditemukan** di proyek saat ini. Jika dibutuhkan, perlu dibangun dari awal, bukan diasumsikan sudah ada.

## 🚀 Quick Start

### Setup Lokal (Development)

```bash
# Clone repository
git clone https://github.com/MSKI5/ManRiskMSKI.git
cd ManRiskMSKI

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
# atau venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Salin/edit file .env (tidak ada .env.example, buat manual sesuai variabel di bagian Environment Variables)
python init_db.py     # Setup awal tabel & data (aman dijalankan berkali-kali)
python app.py

# Frontend Setup (di terminal baru)
cd frontend
npm install
# Edit .env: sesuaikan VITE_API_URL ke backend Anda
npm run dev
```

**Akses:**
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api`
- Health Check: `http://localhost:5000/health`

> Untuk detail deployment ke production, lihat [SETUP_GUIDE.md](./SETUP_GUIDE.md).

## 📚 Dokumentasi

| File | Isi |
|------|-----|
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | Setup & deployment lengkap |
| [docs/PANDUAN_PENGGUNA.md](./docs/PANDUAN_PENGGUNA.md) | Panduan pengguna untuk 5 seksi |
| [docs/PANDUAN_ADMIN.md](./docs/PANDUAN_ADMIN.md) | Panduan tugas rutin Administrator |
| [docs/API_DOCS.md](./docs/API_DOCS.md) | Referensi API lengkap (disusun dari kode aktual) |

## 🔐 Security

- ✅ JWT Authentication — Access token 1 jam, Refresh token 7 hari, dengan blacklist untuk logout
- ✅ Password Hashing (Werkzeug PBKDF2)
- ✅ Reset Password oleh Admin (tanpa email) — password sementara, wajib ganti saat login pertama, ditegakkan oleh middleware global di backend
- ✅ CORS — saat ini **hardcode hanya mengizinkan `http://localhost:5173`** di kode (`app.py`); env var `CORS_ORIGINS` ada di `.env` namun belum dipakai oleh kode. **Perlu diperbaiki sebelum deploy ke domain production.**
- ✅ SQL Injection Prevention (SQLAlchemy ORM)
- ✅ File Upload Validation — deteksi tipe file dari isi file (magic bytes), whitelist MIME type, ukuran maksimal 25 MB, nama file disimpan ulang sebagai UUID
- ✅ Audit Logging — login, register, reset password, ganti password
- ✅ Role-Based Access Control — isolasi data per seksi di level query database
- ⚠️ Rate Limiting — **belum diimplementasikan**, perlu ditambahkan sebelum produksi
- ⚠️ HTTPS/SSL — tergantung platform hosting yang dipilih, tidak ada konfigurasi eksplisit di kode

## 💾 Data Storage

```
📊 Database (PostgreSQL Supabase):
   └─ users                    (akun pengguna, role, section, status password)
   └─ risk_indicators           (25 indikator aktif + 4 indikator nonaktif untuk riwayat)
   └─ risk_assessments          (data Q1-Q4 per indikator per seksi)
   └─ risk_matrix_mapping       (25 baris pemetaan resmi Kemenkeu)
   └─ supporting_documents      (metadata bukti pendukung)
   └─ audit_logs                (jejak rekam aksi pengguna)
   └─ jwt_blacklist             (token yang sudah di-logout)

📁 File Storage (Server Lokal):
   └─ uploads/bukti_pendukung/{uuid}.{ext}
      ⚠️ Tidak persisten di platform PaaS tanpa persistent disk (Railway/Heroku/Render).
         Perlu dipindahkan ke object storage sebelum deploy produksi.
```

## 📞 Support & Contact

Untuk pertanyaan/masalah teknis terkait sistem ini, hubungi tim developer/teknis internal KPPN.

## 📜 License

Internal Use Only - KPPN
All rights reserved © 2026

---

**Dibuat untuk**: KPPN Manajemen Risiko
**Dokumentasi diperbarui**: 21 Juni 2026 (disusun ulang berdasarkan audit kode aktual)
**Status**: 🟡 Dalam Pengembangan — fitur inti berfungsi, beberapa fitur pelaporan lanjutan (Export PDF/ZIP, Verifikasi Admin) masih perlu dibangun