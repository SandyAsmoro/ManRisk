# API Documentation - Sistem Manajemen Risiko KPPN

> Dokumen ini disusun ulang berdasarkan pemeriksaan langsung terhadap kode backend (`routes/auth.py`, `routes/risiko.py`, `routes/dashboard.py`, `routes/matriks.py`, `routes/laporan.py`, `app.py`). Setiap path, method, dan response di bawah ini mencerminkan kode yang benar-benar berjalan, bukan rancangan awal.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Hampir semua endpoint memerlukan JWT **access token** di header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```
Endpoint `POST /auth/login` adalah satu-satunya endpoint publik yang tidak memerlukan token.

---

## 1. Authentication & User Management
*(Blueprint terdaftar di `/api/auth`)*

### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "mski_user",
  "password": "password123"
}
```
**Response sukses (200):**
```json
{
  "status": "success",
  "message": "Login berhasil",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": "uuid",
      "username": "mski_user",
      "full_name": "Nama Pegawai",
      "role": "user",
      "section": "Seksi MSKI",
      "must_change_password": false
    }
  }
}
```
**Error response (401):**
```json
{ "status": "error", "message": "Username atau password salah atau akun nonaktif." }
```
> **Catatan penting untuk frontend:** jika `must_change_password` bernilai `true`, paksa user ke halaman Ganti Password sebelum mengizinkan navigasi ke halaman lain.

---

### Register User Baru (Admin only)
```
POST /auth/register
Authorization: Bearer TOKEN

{
  "username": "new_user",
  "email": "user@kppn.local",
  "password": "password123",
  "full_name": "User Name",
  "role": "user",
  "section": "Seksi MSKI"
}
```
**Response sukses (201):**
```json
{ "status": "success", "message": "Registrasi berhasil. Akun baru berhasil dibuat." }
```
**Error responses:**
- `400` — `{"status":"error","message":"Username, email, dan password wajib diisi."}`
- `400` — `{"status":"error","message":"Username sudah digunakan."}`
- `400` — `{"status":"error","message":"Email sudah digunakan."}`
- `403` — `{"status":"error","message":"Akses ditolak. Hanya Administrator yang diizinkan."}` (jika pemanggil bukan admin)

---

### Reset Password User (Admin only)
```
POST /auth/users/{user_id}/reset-password
Authorization: Bearer TOKEN
```
Tidak ada body yang diperlukan. Sistem otomatis men-generate password sementara 12 karakter dan menandai `must_change_password = true` pada user target.

**Response sukses (200):**
```json
{
  "status": "success",
  "message": "Password berhasil direset. Silakan salin dan berikan kepada user.",
  "temporary_password": "Tmp@8x2kL9zQ"
}
```
> `temporary_password` hanya dikembalikan **sekali** dalam response ini. Tampilkan ke Admin lalu jangan disimpan di state aplikasi lebih lama dari yang diperlukan.

**Error responses:**
- `403` — `{"status":"error","message":"HTTP 403 Akses Ditolak: Hanya Admin yang dapat mereset password."}`
- `404` — `{"status":"error","message":"User tidak ditemukan."}`

---

### Ganti Password (Diri Sendiri)
```
PUT /auth/change-password
Authorization: Bearer TOKEN

{
  "old_password": "Tmp@8x2kL9zQ",
  "new_password": "PasswordBaruSaya123",
  "confirm_password": "PasswordBaruSaya123"
}
```
Endpoint ini dipakai baik untuk ganti password sukarela maupun untuk memenuhi paksaan `must_change_password`. Setelah berhasil, flag tersebut otomatis di-set `false`.

**Response sukses (200):**
```json
{ "status": "success", "message": "Password Anda berhasil diperbarui." }
```
**Error responses:**
- `400` — `{"status":"error","message":"Seluruh kolom password wajib diisi."}`
- `400` — `{"status":"error","message":"Konfirmasi password baru tidak cocok."}`
- `400` — `{"status":"error","message":"Password lama yang Anda masukkan salah."}`

---

### Logout
```
POST /auth/logout
Authorization: Bearer TOKEN
```
Memasukkan JTI token saat ini ke blacklist sehingga token tidak bisa dipakai lagi meski belum expired.

**Response sukses (200):**
```json
{ "status": "success", "message": "Sesi diakhiri." }
```

---

### Refresh Access Token
```
POST /auth/refresh
Authorization: Bearer REFRESH_TOKEN
```
Gunakan **refresh token** (bukan access token) yang diperoleh saat login, di header Authorization.

**Response sukses (200):**
```json
{ "status": "success", "data": { "token": "eyJhbGciOiJIUzI1NiIs..." } }
```

---

### Ambil Profil Sendiri
```
GET /auth/me
Authorization: Bearer TOKEN
```
**Response sukses (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid", "username": "mski_user", "email": "mski@kppn.local",
    "full_name": "Nama Pegawai", "role": "user", "section": "Seksi MSKI"
  }
}
```

---

### Update Profil Sendiri
```
PUT /auth/me
Authorization: Bearer TOKEN

{ "full_name": "Nama Baru" }
```
> Saat ini hanya field `full_name` yang dapat diubah lewat endpoint ini.

**Response sukses (200):**
```json
{ "status": "success", "message": "Profil berhasil diubah." }
```

---

### Daftar Semua User (Admin only)
```
GET /auth/users
Authorization: Bearer TOKEN
```
**Response sukses (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid", "username": "mski_user", "email": "mski@kppn.local",
      "full_name": "Nama Pegawai", "role": "user", "section": "Seksi MSKI",
      "is_active": true, "must_change_password": false
    }
  ]
}
```

---

### Update Data User Lain (Admin only)
```
PUT /auth/users/{user_id}
Authorization: Bearer TOKEN

{
  "full_name": "Nama Diperbarui",
  "role": "user",
  "section": "Seksi Bank"
}
```
Ketiga field bersifat opsional — hanya field yang dikirim yang akan diubah.

**Response sukses (200):**
```json
{ "status": "success", "message": "User berhasil diperbarui." }
```

---

### Nonaktifkan User / Soft-Delete (Admin only)
```
DELETE /auth/users/{user_id}
Authorization: Bearer TOKEN
```
Men-set `is_active = false` pada user target — **bukan** menghapus baris secara permanen dari database.

**Response sukses (200):**
```json
{ "status": "success", "message": "User dinonaktifkan." }
```
**Error response (400):**
```json
{ "status": "error", "message": "Tidak bisa menonaktifkan diri sendiri." }
```

---

## 2. Risk Indicators & Assessments
*(Blueprint terdaftar di `/api/risiko`)*

### Get Semua Indikator Aktif
```
GET /risiko/indicators
Authorization: Bearer TOKEN
```
**Response sukses (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "code": "1a-CP-01",
      "name": "Nilai Kinerja Pelaksanaan Anggaran K/L",
      "pic": "Seksi MSKI",
      "secondary_pics": null
    }
  ]
}
```
> Hanya mengembalikan indikator dengan `is_active = true` (total 25 setelah perbaikan data — lihat catatan inkonsistensi jumlah indikator).

---

### Get Daftar Assessment (dengan filter)
```
GET /risiko/assessments?quarter=Q1&year=2026&section=Seksi%20MSKI
Authorization: Bearer TOKEN
```
Parameter query (semuanya opsional):
- `quarter` — `Q1` | `Q2` | `Q3` | `Q4`
- `year` — tahun (contoh `2026`)
- `section` — hanya berlaku untuk Admin, untuk memfilter ke seksi tertentu

**Perilaku otomatis berdasarkan role:**
- User biasa: hanya melihat assessment milik seksinya sendiri **atau** indikator di mana seksinya tercatat sebagai `secondary_pics` (Indikator Bersama).
- Admin: melihat semua seksi, kecuali memberi filter `section` secara eksplisit.

**Response sukses (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "indicator_id": 1,
      "risk_value": 14,
      "risk_category": "Kuning",
      "section": "Seksi MSKI",
      "quarter": "Q1",
      "year": 2026,
      "status": "draft"
    }
  ]
}
```

---

### Simpan Data Assessment Baru (Draft)
```
POST /risiko/assessment
Authorization: Bearer TOKEN

{
  "indicator_id": 1,
  "quarter": "Q1",
  "frequency": 3,
  "impact": 4,
  "change_reason": "Dilakukan edukasi satker...",
  "mitigation_action": "Implementasi validasi otomatis"
}
```
> **Catatan path**: endpoint create memakai bentuk **tunggal** `/assessment`, bukan `/assessments`. Ini berbeda dari endpoint list (`/assessments`, bentuk jamak) — perhatikan baik-baik saat mengintegrasikan frontend.

Sistem otomatis:
1. Menolak dengan `403` jika quarter sedang terkunci (lihat tabel jadwal di bagian Quarter Locking) — **kecuali** pemanggil adalah Admin.
2. Mengambil `risk_value` dan `risk_category` resmi dari tabel `risk_matrix_mapping` berdasarkan kombinasi `frequency` × `impact` (sesuai Matriks Kemenkeu, bukan perkalian sederhana).
3. Mencari assessment quarter sebelumnya secara otomatis untuk menghitung `risk_change`.
4. `year` otomatis diambil dari tahun berjalan (tidak perlu dikirim dari client).

**Response sukses (200):**
```json
{ "status": "success", "message": "Data berhasil disimpan", "assessment_id": "uuid" }
```
**Error responses:**
- `403` — `{"status":"error","message":"HTTP 403: Periode pelaporan Q1 sudah dikunci."}`
- `400` — `{"status":"error","message":"Kombinasi nilai frekuensi dan dampak risiko tidak valid."}`

---

### Get / Update Satu Assessment
```
GET /risiko/assessment/{assessment_id}
PUT /risiko/assessment/{assessment_id}
Authorization: Bearer TOKEN
```
Akses diverifikasi lewat `check_section_access()` — hanya seksi pemilik data atau Admin yang diizinkan.

**GET — Response sukses (200):**
```json
{
  "status": "success",
  "data": {
    "id": "uuid", "indicator_id": 1, "frequency": 3, "impact": 4,
    "risk_value": 14, "risk_category": "Kuning",
    "section": "Seksi MSKI", "quarter": "Q1", "year": 2026, "status": "draft",
    "supporting_documents": [
      { "id": "uuid", "original_filename": "Laporan_Edukasi.pdf" }
    ]
  }
}
```

**PUT — Body:**
```json
{ "frequency": 2, "impact": 5 }
```
Hanya `frequency` dan `impact` yang diproses oleh endpoint ini — keduanya wajib dikirim bersamaan agar nilai risiko dihitung ulang.

**Error response (403) — jika assessment sudah berstatus submitted:**
```json
{ "status": "error", "message": "Data sudah dikirim (submitted) dan tidak dapat diubah lagi." }
```

---

### Batch Submit (Kirim Final Satu Quarter Penuh)
```
POST /risiko/assessments/batch-submit
Authorization: Bearer TOKEN

{ "quarter": "Q1", "year": 2026 }
```
Memvalidasi apakah **seluruh indikator aktif** (25 indikator) untuk seksi pemanggil sudah memiliki data assessment pada quarter & tahun tersebut. Admin dapat menambahkan `"section": "Seksi Bank"` di body untuk men-submit-kan atas nama seksi lain.

**Response sukses (200):**
```json
{
  "status": "success",
  "message": "Batch submit berhasil! Sebanyak 25 data asesmen risiko seksi Seksi MSKI periode Q1 2026 telah resmi dikirim dan dikunci.",
  "summary": { "total_submitted": 25, "newly_locked": 25 }
}
```
**Error response (400) — jika ada indikator yang belum diisi:**
```json
{
  "status": "error",
  "message": "Gagal mengirim berkas final. Terdapat 3 dari 25 indikator risiko yang belum diisi untuk seksi Anda.",
  "missing_indicators": ["[3b-N-02] Indeks Kualitas Penyelesaian SP2D...", "..."]
}
```

---

### Hapus Dokumen Pendukung
```
DELETE /risiko/documents/{doc_id}
Authorization: Bearer TOKEN
```
Menghapus file fisik dari server sekaligus baris metadata di database. Hanya pemilik seksi atau Admin yang diizinkan.

**Response sukses (200):**
```json
{ "status": "success", "message": "Dokumen berhasil dihapus." }
```
**Error response (403):**
```json
{ "status": "error", "message": "HTTP 403 Akses Ditolak" }
```

---

### Download Dokumen Pendukung (via Risiko)
```
GET /risiko/documents/{doc_id}/download
Authorization: Bearer TOKEN
```
Mengembalikan file sebagai attachment dengan nama file asli (`original_filename`), bukan nama UUID yang tersimpan di server.

---

## 3. Dashboard Summary
*(Blueprint terdaftar di `/api/dashboard`)*

### Ringkasan Jumlah Indikator per Kategori Warna
```
GET /dashboard/summary?quarter=Q1&year=2026
Authorization: Bearer TOKEN
```
User biasa otomatis terfilter ke seksinya sendiri; Admin melihat agregat seluruh seksi.

**Response sukses (200):**
```json
{
  "status": "success",
  "data": { "Biru": 3, "Hijau": 6, "Kuning": 8, "Jingga": 5, "Merah": 3 }
}
```
> Frontend Dashboard memanggil endpoint ini setiap 30 detik secara otomatis (polling) untuk efek "real-time update".

---

## 4. Matrix Summary
*(Blueprint terdaftar di `/api/matriks`)*

### Ringkasan Kategori per Quarter (Lintas Seksi)
```
GET /matriks/summary/{quarter}
Authorization: Bearer TOKEN
```
Contoh: `GET /matriks/summary/Q1`. **Endpoint ini tidak menerima parameter `year`** — secara default menghitung seluruh data quarter tersebut tanpa filter tahun, dan tidak memfilter berdasarkan section pemanggil (selalu agregat semua seksi).

**Response sukses (200):**
```json
{
  "status": "success",
  "data": { "Biru": 4, "Hijau": 7, "Kuning": 9, "Jingga": 3, "Merah": 2 }
}
```

---

## 5. Document Upload
*(Blueprint terdaftar di `/api/laporan`)*

### Upload Dokumen Pendukung
```
POST /laporan/upload
Authorization: Bearer TOKEN
Content-Type: multipart/form-data

assessment_id: uuid
file: [binary file]
```
Validasi yang diterapkan:
- Ukuran maksimal **25 MB** per file (`MAX_FILE_SIZE`).
- Tipe file divalidasi dari **isi file** (magic bytes), bukan hanya ekstensi nama file. Whitelist: PDF, DOC, DOCX, XLS, XLSX, PNG, JPEG, ZIP.
- Nama file disimpan ulang sebagai UUID acak di server (`stored_filename`), nama asli tetap disimpan terpisah (`original_filename`) untuk ditampilkan ke user.

**Response sukses (201):**
```json
{ "status": "success", "message": "Dokumen berhasil diunggah dengan aman!" }
```
**Error responses:**
- `413` — `{"status":"error","message":"Ukuran file maksimal 25MB"}`
- `400` — `{"status":"error","message":"Tipe file ditolak (application/x-msdownload). Hanya dokumen, gambar, dan ZIP yang diizinkan."}`
- `400` — `{"status":"error","message":"ID Assessment diperlukan"}`

> **Inkonsistensi yang perlu diperbaiki**: form di `InputDataPage.vue` menampilkan teks "Maksimal 5MB" kepada user, padahal backend menegakkan batas 25MB. Selaraskan salah satu nilai ini agar tidak membingungkan pengguna.

---

### Download Dokumen (via Laporan)
```
GET /laporan/download/{filename}
Authorization: Bearer TOKEN
```
> Endpoint ini menggunakan **nama file yang tersimpan di server** (UUID), bukan ID dokumen — berbeda dari `GET /risiko/documents/{doc_id}/download` yang menggunakan ID dan mengembalikan nama file asli. Disarankan memakai endpoint `/risiko/documents/{doc_id}/download` dari sisi frontend karena lebih aman (tidak mengekspos nama file fisik di URL) dan lebih konsisten dengan validasi akses per-seksi.

---

## ⚠️ Endpoint yang Dipanggil Frontend Tapi Belum Ada di Backend

Ditemukan saat audit kode bahwa frontend memanggil endpoint berikut, namun **belum ada implementasinya** di backend manapun:

```
GET /laporan/export?type=csv
GET /laporan/export?type=excel
```
Dipanggil dari `LaporanPage.vue` (tombol "Export CSV" dan "Export Excel"), tapi tidak ada route yang cocok di `routes/laporan.py`. Memanggil tombol ini di frontend saat ini akan menghasilkan error `404 Not Found`. Endpoint ini perlu dibangun di backend sebelum fitur Laporan & Rekap benar-benar berfungsi.

---

## ⚠️ Fitur yang Disebut di Dokumentasi Lama Tapi Tidak Ada di Kode

Untuk mencegah AI agent atau developer lain salah asumsi, berikut fitur yang **tidak ditemukan** di backend manapun meski pernah didokumentasikan sebelumnya:

- `POST /admin/assessments/{id}/verify` — **tidak ada**. Blueprint `admin_bp` di `routes/admin.py` bahkan tidak terdaftar (`register_blueprint`) di `app.py`, sehingga seluruh path `/api/admin/*` tidak aktif sama sekali.
- Export PDF dan Export ZIP — **tidak ada** di backend manapun.
- Endpoint reset password mandiri via email (`/auth/forgot-password`) — **tidak ada**, dan **tidak diperlukan**, karena sistem ini menggunakan mekanisme reset oleh Admin (`POST /auth/users/{id}/reset-password`).

---

## Error Responses (Format Umum)

```json
{
  "status": "error",
  "message": "Error description",
  "code": 400
}
```
> Catatan: tidak semua endpoint mengembalikan field `code` di body JSON — sebagian hanya mengandalkan HTTP status code itu sendiri. Periksa HTTP status code, bukan hanya body JSON, saat menangani error di frontend.

Kode error yang umum dipakai di backend ini:
- `400` — Bad Request (validasi input gagal)
- `401` — Unauthorized (token tidak valid/tidak ada, atau kredensial login salah)
- `403` — Forbidden (role tidak sesuai, atau quarter terkunci, atau data sudah submitted)
- `404` — Not Found
- `413` — Payload Too Large (file upload melebihi batas)
- `500` — Internal Server Error

## Rate Limiting & Pagination

Belum diimplementasikan di backend versi ini. Tidak ada middleware rate-limiting, dan endpoint list (`GET /risiko/assessments`, `GET /auth/users`) mengembalikan seluruh hasil tanpa parameter `page`/`per_page`. Pertimbangkan menambahkan ini sebelum jumlah data bertambah signifikan.