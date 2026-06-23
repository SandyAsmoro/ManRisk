# 🚀 Setup & Deployment Guide

> Panduan ini disusun ulang berdasarkan kode aktual di `backend/` dan `frontend/`. Beberapa langkah di rancangan awal (Heroku, GitHub Pages, `docker-compose`, `nginx.conf`) tidak sesuai dengan apa yang sebenarnya tersedia di proyek ini — bagian tersebut diganti dengan langkah yang benar-benar berlaku.

## Quick Start (Local Development)

### Prerequisites
```bash
Node.js v18+
Python 3.11+
Akun Supabase (gratis)
Git
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
# atau venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Buat file `.env` di dalam folder `backend/` (tidak ada `.env.example` di proyek ini, buat manual dengan isi sesuai bagian **Environment Variables** di bawah).

```bash
python init_db.py   # Setup tabel & data awal — aman dijalankan berkali-kali (idempoten)
python app.py
```

`init_db.py` akan:
- Membuat tabel jika belum ada (skip jika sudah ada — tidak error)
- Mengisi data 25 indikator + matriks resmi jika belum ada (skip jika sudah ada — tidak duplikat)
- Membuat akun admin default jika belum ada (skip jika sudah ada)

> **Catatan password admin default**: hash password admin tersimpan menggunakan `werkzeug.security.generate_password_hash`. Jika Anda tidak tahu password plaintext-nya setelah `init_db.py` dijalankan, generate hash baru secara manual:
> ```bash
> python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('PasswordBaruAnda123!'))"
> ```
> Lalu update kolom `password_hash` langsung di Supabase Dashboard → Table Editor → tabel `users`.

### Frontend Setup
```bash
cd frontend
npm install
```

Buat/edit file `.env` di folder `frontend/`:
```
VITE_API_URL=http://localhost:5000/api
VITE_APP_NAME=Sistem Manajemen Risiko KPPN
VITE_APP_VERSION=1.0.0
VITE_DEBUG=true
```

```bash
npm run dev
```

**Akses:**
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000/api`
- Health Check: `http://localhost:5000/health`

---

## Database Setup (Supabase)

1. Buat akun di https://supabase.com dan buat project baru.
2. Di Supabase Dashboard, buka **Project Settings → Database → Connection String**, pilih mode **Connection Pooling (PgBouncer)** — bukan direct connection. Salin connection string-nya (biasanya menggunakan port `6543`).
3. Tempel ke `DATABASE_URL` di file `.env` backend. Mode pooler **wajib** dipakai karena tier gratis Supabase membatasi jumlah koneksi langsung.
4. Jalankan `python init_db.py` dari folder `backend/` untuk membuat seluruh tabel dan mengisi data awal — **tidak perlu** menjalankan file `.sql` secara manual lewat SQL Editor seperti pada rancangan awal, kecuali Anda ingin meninjau/menjalankan skrip schema secara manual untuk keperluan audit.

> Jika Anda tetap ingin menjalankan SQL secara manual (misalnya untuk server selain Supabase), urutannya: `database/schema.sql` lalu `database/initial_data.sql`. Pastikan `initial_data.sql` yang dipakai sudah memuat 25 baris `risk_matrix_mapping` resmi Kemenkeu, bukan versi lama yang nilainya keliru.

---

## Deployment (Stack Gratis yang Direkomendasikan)

Stack berikut dipilih agar seluruh sistem dapat berjalan tanpa biaya untuk skala internal KPPN (jumlah user kecil):

| Komponen | Platform | Catatan |
|---|---|---|
| Frontend | **Netlify** | Build statis dari `vite build`, tidak ada batasan berarti di tier gratis |
| Backend | **Railway** | Tier gratis ($5 credit/bulan), lebih cocok untuk proyek baru dibanding Heroku |
| Database | **Supabase PostgreSQL** | Tier gratis, gunakan mode pooler |
| File Storage | ⚠️ **Belum dikonfigurasi** | Lihat peringatan penting di bawah |

### ⚠️ Peringatan Penting: File Storage Belum Persisten

Backend saat ini menyimpan dokumen pendukung ke disk lokal server (`uploads/bukti_pendukung/`). Platform seperti **Railway tidak menyediakan persistent disk** secara default — file yang diupload akan **hilang setiap kali backend di-redeploy atau restart**.

**Sebelum go-live produksi**, pindahkan logic upload di `backend/routes/laporan.py` agar menyimpan file ke object storage (misalnya Supabase Storage) alih-alih `os.path.join(os.getcwd(), 'uploads', ...)`. Untuk development lokal atau demo jangka pendek, disk lokal masih bisa dipakai sementara.

### Backend: Railway

```bash
# Install Railway CLI jika belum
npm install -g @railway/cli

railway login
railway init
railway up
```

Di Railway Dashboard, set environment variables sesuai bagian **Environment Variables** di bawah (`DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, dst). Railway otomatis mendeteksi `Dockerfile` di folder `backend/` dan menjalankannya — termasuk `HEALTHCHECK` yang sudah mengarah ke endpoint `/health`.

> Railway juga otomatis menyediakan variabel `PORT` — kode `app.py` sudah membaca `os.getenv('PORT', 5000)` sehingga kompatibel tanpa perubahan.

### Frontend: Netlify

```bash
cd frontend
npm run build
```

Hubungkan repository ke Netlify, atau gunakan Netlify CLI:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

Set environment variable di Netlify Dashboard (**Site settings → Environment variables**):
```
VITE_API_URL=https://your-backend.up.railway.app/api
VITE_APP_NAME=Sistem Manajemen Risiko KPPN
```

### ⚠️ Langkah Wajib Setelah Deploy: Perbaiki CORS

Kode `backend/app.py` saat ini **hardcode** mengizinkan origin `http://localhost:5173` saja:

```python
CORS(app,
     resources={r"/api/*": {"origins": "http://localhost:5173"}},
     ...)
```

Setelah frontend live di Netlify, **request dari domain production akan ditolak CORS** kecuali baris ini diperbarui. Ganti menjadi:

```python
CORS(app,
     resources={r"/api/*": {"origins": os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')}},
     ...)
```

Lalu set `CORS_ORIGINS=https://your-app.netlify.app` di environment variable Railway. Variabel `CORS_ORIGINS` sudah ada di `.env` proyek ini namun belum benar-benar dipakai oleh kode — perbaikan ini menyambungkannya.

---

## User Setup

### Membuat User Pertama (Admin)

Setelah `init_db.py` dijalankan, akun admin default akan tersedia (lihat catatan password di atas). Untuk membuat admin tambahan atau mengganti kredensial, gunakan endpoint register setelah login sebagai admin yang sudah ada:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN_ADMIN_YANG_SUDAH_LOGIN" \
  -d '{
    "username": "admin2",
    "email": "admin2@kppn.local",
    "password": "AdminSecure2026!",
    "full_name": "Administrator Kedua",
    "role": "admin"
  }'
```

> Endpoint `/auth/register` **wajib** disertai token Admin yang valid — tidak bisa diakses tanpa otentikasi (lihat `API_DOCS.md` untuk detail validasi).

### Membuat User per Seksi

Ulangi proses register di atas untuk setiap seksi, dengan `"role": "user"` dan `"section"` sesuai salah satu dari: `Seksi MSKI`, `Seksi Bank`, `Seksi PD`, `Seksi Vera`, `Subbagian Umum`.

---

## Environment Variables

### Backend (`backend/.env`)

```bash
# Connection string Supabase — WAJIB pakai mode Pooler (PgBouncer), port 6543
DATABASE_URL=postgresql://postgres.xxxxx:PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres

# Generate dengan: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=ganti-dengan-hasil-generate-acak
JWT_SECRET_KEY=ganti-dengan-hasil-generate-acak-yang-berbeda

FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000

# Domain frontend yang diizinkan mengakses API (lihat bagian perbaikan CORS di atas)
CORS_ORIGINS=https://your-app.netlify.app
```

> **Jangan gunakan nilai placeholder apa adanya.** Generate `SECRET_KEY` dan `JWT_SECRET_KEY` dengan perintah Python di atas — jalankan dua kali untuk mendapat dua nilai acak yang berbeda.

### Frontend (`frontend/.env`)

```bash
VITE_API_URL=http://localhost:5000/api
VITE_APP_NAME=Sistem Manajemen Risiko KPPN
VITE_APP_VERSION=1.0.0
VITE_DEBUG=true
```

Saat deploy ke production, ubah `VITE_API_URL` ke URL backend Railway dan `VITE_DEBUG=false`.

---

## Troubleshooting

### Database Connection Error
- Pastikan `DATABASE_URL` memakai mode **Pooler** (port `6543`), bukan direct connection (port `5432`) — tier gratis Supabase membatasi koneksi langsung.
- Test koneksi: `psql "your_connection_string"`

### CORS Error setelah Deploy
- Lihat bagian "⚠️ Langkah Wajib Setelah Deploy: Perbaiki CORS" di atas — ini adalah penyebab paling umum error CORS setelah frontend dideploy ke Netlify.

### Error 403 "Wajib ganti password terlebih dahulu"
- Ini bukan bug — middleware `enforce_password_change` di `app.py` sengaja memblokir semua endpoint (kecuali login/logout/refresh/change-password) selagi `must_change_password = true` pada akun tersebut. Arahkan user untuk memanggil `PUT /auth/change-password` terlebih dahulu.

### File Upload Gagal / Hilang Setelah Redeploy
- Lihat peringatan "File Storage Belum Persisten" di atas. Ini bukan bug aplikasi, melainkan keterbatasan disk lokal di platform PaaS.

### Import Error (Python)
- Pastikan virtual environment sudah diaktifkan
- Jalankan ulang: `pip install -r requirements.txt`
- `python-magic-bin` di `requirements.txt` ditujukan untuk Windows; jika deploy di Linux (Railway), pastikan library sistem `libmagic` tersedia di image Docker (Dockerfile bawaan sudah menanganinya).

---

## Backup & Restore

### Backup Manual dari Supabase

```bash
pg_dump "postgresql://postgres.xxxxx:PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres" > database_backup_$(date +%Y%m%d).sql
```

> Gunakan port `5432` (bukan `6543`) khusus untuk `pg_dump`, karena pooler PgBouncer di port 6543 tidak selalu mendukung seluruh operasi yang dibutuhkan `pg_dump`.

### Restore

```bash
psql "your_connection_string" < database_backup_20260621.sql
```

Disarankan melakukan backup manual ini di akhir setiap quarter (lihat `PANDUAN_ADMIN.md` untuk SOP lengkap), sebagai pelengkap backup otomatis yang sudah disediakan Supabase.

## Support
Hubungi tim developer/teknis internal KPPN untuk bantuan setup lebih lanjut.