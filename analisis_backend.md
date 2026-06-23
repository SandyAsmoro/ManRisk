# 🔍 Analisis Kekurangan Backend — ManRiskMSKI

> **Kesimpulan Utama:** Backend Flask **bisa dijalankan** secara teknis, namun menghasilkan 404 karena **hampir semua route API tidak ada** — `app.py` hanya skeleton tanpa implementasi endpoint. Ada pula beberapa bug tambahan.

---

## 🔴 Masalah Kritis (Langsung Menyebabkan 404)

### 1. Route API Tidak Diimplementasikan

Ini adalah **penyebab utama** error 404. `app.py` hanya mendaftarkan **3 route**:

| Route | Status |
|-------|--------|
| `/health` | ✅ Ada (tapi bug — lihat bawah) |
| `/api/info` | ✅ Ada |
| `/static/<path>` | ✅ Auto (Flask) |

Padahal, di `/api/info` sendiri diklaim ada endpoint berikut — **yang semuanya TIDAK ADA**:

| Endpoint yang Dijanjikan | Status |
|--------------------------|--------|
| `/api/auth` (login, register, dll) | ❌ **TIDAK ADA** |
| `/api/dashboard` | ❌ **TIDAK ADA** |
| `/api/risiko` | ❌ **TIDAK ADA** |
| `/api/matriks` | ❌ **TIDAK ADA** |
| `/api/laporan` | ❌ **TIDAK ADA** |
| `/api/admin` | ❌ **TIDAK ADA** |

**Semua request ke endpoint tersebut akan menghasilkan `404 Resource not found`.**

---

## 🟠 Bug Kode (Error Saat Runtime)

### 2. SQLAlchemy 2.0 Incompatibility di `/health`

**File:** `backend/app.py`, baris 91

```python
# ❌ SALAH — cara lama SQLAlchemy 1.x
db.session.execute('SELECT 1')

# ✅ BENAR — SQLAlchemy 2.0 wajib pakai text()
from sqlalchemy import text
db.session.execute(text('SELECT 1'))
```

**Akibat:** Endpoint `/health` selalu return `500 unhealthy` meski koneksi DB berhasil.

**Error yang muncul:**
```
Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

---

### 3. Mismatch Nama Variabel JWT di `.env`

**File:** `backend/.env` vs `backend/app.py`

| Lokasi | Nama Key |
|--------|----------|
| `.env` | `JWT_SECRET_KEY` |
| `app.py` baris 46 | `os.getenv('JWT_SECRET', ...)` |

`app.py` membaca `JWT_SECRET`, tapi `.env` menyimpan `JWT_SECRET_KEY`.  
**Akibat:** Flask menggunakan fallback default `'super-secret-jwt-key'` — bukan nilai dari `.env`. Ini **risiko keamanan serius** di production.

---

### 4. `gunicorn` Tidak Terinstall

**File:** `backend/Dockerfile`, baris 31

```dockerfile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

`gunicorn` **tidak ada** di `requirements.txt` dan **tidak terinstall** di venv.

**Akibat:**
- Docker container akan **crash** saat start karena `gunicorn` tidak ditemukan.
- Mode lokal (`python app.py`) bisa jalan, tapi Docker deploy gagal.

---

## 🟡 Masalah Arsitektur (Menghambat Fungsionalitas)

### 5. Tidak Ada Model Database

`app.py` menginisialisasi `SQLAlchemy` dan `Flask-Migrate`, tapi **tidak ada satu pun model** yang didefinisikan:

```python
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# ... tidak ada class User, RiskIndicator, dll
```

**Akibat:**
- `db.create_all()` tidak membuat tabel apapun.
- `flask db migrate` tidak menghasilkan migrasi.
- Semua fitur CRUD tidak bisa dibuat karena tidak ada model ORM.

Schema database **sudah ada** di `database/schema.sql`, tapi tidak ada padanan model Python-nya.

---

### 6. Python 3.13 vs Flask 2.3.3 — Potensi Inkompatibilitas

**Versi terdeteksi:** Python `3.13.7` dengan Flask `2.3.3`

Flask 2.3.3 dirilis sebelum Python 3.13 stabil. Beberapa internal API bisa berubah.

**Rekomendasi:** Upgrade ke Flask `3.x` yang mendukung Python 3.13 secara resmi:
```
Flask>=3.0.0
Werkzeug>=3.0.0
```

---

### 7. `SECRET_KEY` Tidak Digunakan Flask

**File:** `backend/.env` baris 4, `backend/app.py`

`.env` mendefinisikan `SECRET_KEY=manrisk-secret-key-kppn-2024-abcdef` namun `app.py` **tidak pernah membacanya**:

```python
# ❌ Tidak ada baris ini di app.py:
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback')
```

Flask membutuhkan `SECRET_KEY` untuk session management. Tanpanya, fitur session Flask tidak aman.

---

## 📋 Ringkasan & Prioritas Perbaikan

| # | Masalah | Tingkat | Tindakan |
|---|---------|---------|---------|
| 1 | Semua route `/api/*` tidak ada | 🔴 KRITIS | Buat Blueprint + Controller untuk auth, risiko, dashboard, dll |
| 2 | Bug `text('SELECT 1')` di health check | 🔴 KRITIS | Ganti `db.session.execute('SELECT 1')` → `db.session.execute(text('SELECT 1'))` |
| 3 | `JWT_SECRET_KEY` vs `JWT_SECRET` mismatch | 🟠 TINGGI | Samakan nama key di `.env` atau `app.py` |
| 4 | `gunicorn` tidak di `requirements.txt` | 🟠 TINGGI | Tambah `gunicorn` ke `requirements.txt` |
| 5 | Tidak ada model ORM/database | 🟠 TINGGI | Buat `models.py` berisi `User`, `RiskIndicator`, dll |
| 6 | Flask 2.3 + Python 3.13 | 🟡 SEDANG | Upgrade Flask ke versi 3.x |
| 7 | `SECRET_KEY` tidak dikonfigurasi | 🟡 SEDANG | Tambah `app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')` |

---

## ✅ Yang Sudah Berjalan Dengan Baik

- Instalasi semua package Python (Flask, SQLAlchemy, JWT, CORS, Migrate) ✅
- Koneksi ke database Supabase berhasil ✅
- Environment `.env` terbaca dengan benar ✅
- Error handler 404 & 500 terdefinisi ✅
- Struktur folder project sudah rapi ✅
