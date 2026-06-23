# Panduan Administrator - Sistem Manajemen Risiko KPPN

Dokumen ini ditujukan khusus untuk pengguna dengan hak akses **Administrator**. Admin bertanggung jawab atas pengelolaan akun pegawai, pemantauan seluruh data seksi, peninjauan data yang sudah dikirim final, serta penyusunan laporan untuk Kanwil/Pusat.

---

## 1. Login sebagai Admin

1. Buka halaman login aplikasi.
2. Masukkan `Username` dan `Password` akun berstatus Administrator.
3. Sistem akan mengarahkan Anda ke Dashboard utama.
4. Setelah login, menu sidebar Anda akan menampilkan dua menu tambahan yang tidak terlihat oleh user biasa: **"Tambah User"** dan **"Kelola User"**.

---

## 2. Kelola User (Manajemen Pengguna)

Sebagai admin, Anda bertanggung jawab penuh atas akses sistem.

### Menambah User Baru
1. Klik menu **"Tambah User"** di sidebar.
2. Isi formulir: username, email, password awal, nama lengkap, role (`admin` atau `user`), dan seksi (Seksi MSKI / Seksi Bank / Seksi PD / Seksi Vera / Subbagian Umum).
3. Klik submit. Akun baru langsung aktif dan bisa digunakan untuk login.

### Mereset Password User
Jika seorang pegawai lupa password dan menghubungi Anda secara langsung (telepon/WA/tatap muka):

1. Buka menu **"Kelola User"**.
2. Cari nama/username pegawai tersebut di tabel daftar pengguna.
3. Klik tombol oranye **"Reset Password"** pada baris user tersebut.
4. Konfirmasi tindakan saat muncul dialog konfirmasi.
5. Sistem akan menampilkan modal berisi **Password Sementara** (kombinasi acak 12 karakter).
6. **Catat atau screenshot password ini sekarang** — modal ini hanya tampil satu kali dan password tidak dapat dilihat ulang setelah modal ditutup.
7. Sampaikan password sementara tersebut kepada pegawai melalui jalur komunikasi yang aman (telepon/WA pribadi, bukan ditulis di tempat umum).
8. Informasikan kepada pegawai bahwa saat mereka login dengan password sementara ini, sistem akan **otomatis memaksa mereka membuat password baru** sebelum bisa mengakses halaman lain.

### Mengelola Akun Lain
Dari tabel di menu **Kelola User**, Anda juga dapat melihat status setiap pengguna: nama, seksi, role, dan status password (apakah masih menunggu diganti).

**Catatan keterbatasan versi ini:** fitur edit profil/role pengguna lain dan nonaktifkan akun (soft-delete) tersedia di tingkat API backend, namun belum semuanya memiliki tombol khusus di tampilan tabel Kelola User. Jika Anda perlu mengubah role, seksi, atau menonaktifkan akun seorang pegawai (misalnya karena mutasi/pensiun) dan tidak menemukan tombolnya di UI, hubungi tim teknis/developer untuk melakukan perubahan langsung melalui database atau API.

---

## 3. Memantau & Meninjau Data Assessment (Tugas Utama Setiap Akhir Kuartal)

Ini adalah tugas rutin Anda di setiap akhir kuartal — memastikan seluruh seksi sudah mengisi data dengan benar sebelum direkap menjadi laporan resmi.

### Yang Harus Dilakukan Admin:

**Langkah 1 — Pantau status pengisian per seksi**
Buka **Dashboard**, pilih quarter yang sedang berjalan dari dropdown Periode. Perhatikan kartu ringkasan kategori warna dan tabel daftar indikator untuk melihat gambaran umum sebaran risiko di seluruh KPPN.

**Langkah 2 — Tagih seksi yang belum mengisi**
Sistem akan menolak permintaan **Kirim Final (Batch Submit)** dari seksi manapun yang datanya belum lengkap (kurang dari 25 indikator). Jika mendekati tanggal pengunci quarter (lihat tabel jadwal di bawah) namun seksi tertentu belum submit, hubungi PIC seksi tersebut secara langsung untuk segera melengkapi dan submit.

| Quarter | Periode | Tenggat Kirim Final |
|---|---|---|
| Q1 | Januari–Maret | 31 Maret, 23:59 |
| Q2 | April–Juni | 30 Juni, 23:59 |
| Q3 | Juli–September | 30 September, 23:59 |
| Q4 | Oktober–Desember | 31 Desember, 23:59 |

**Langkah 3 — Tinjau kewajaran data yang sudah disubmit**
Setelah seksi melakukan Batch Submit, datanya berstatus **"Submitted"** dan terkunci secara otomatis dari sisi user — mereka tidak bisa mengubahnya lagi. Sebagai Admin, lakukan peninjauan manual atas kewajaran nilai Frekuensi/Dampak yang dilaporkan:
- Bandingkan dengan data quarter sebelumnya — apakah ada lonjakan/penurunan ekstrem yang tidak wajar?
- Periksa apakah Tindakan Mitigasi (jika diisi) relevan dengan perubahan nilai risiko.
- Periksa bukti pendukung yang diupload (jika ada) untuk indikator dengan kategori Jingga/Merah.

**Langkah 4 — Koreksi data jika ditemukan kesalahan**
Karena Admin memiliki hak akses istimewa untuk bypass quarter-lock, Anda dapat mengoreksi data milik seksi manapun kapan saja jika ditemukan kesalahan input, tanpa harus menunggu quarter berikutnya dibuka.

**Catatan keterbatasan versi ini:** sistem saat ini **belum memiliki status "Verified" maupun tombol Approve/Reject** yang terpisah dari status Draft/Submitted. Proses peninjauan kewajaran data (Langkah 3) saat ini bersifat manual berdasarkan komunikasi Admin dengan seksi terkait, bukan alur approval formal bertahap di dalam sistem. Catat hasil tinjauan Anda secara manual (misalnya di catatan internal/email) sampai fitur status Verified tersedia di pembaruan sistem berikutnya.

---

## 4. Laporan & Ekspor Data

Buka menu **Laporan & Rekap**, pilih filter Kuartal dan Tahun, lalu unduh data sesuai kebutuhan Anda:

### Yang Tersedia Saat Ini
- **Export CSV** — mengunduh seluruh data rekapitulasi 25 indikator dalam format `.csv`, cocok untuk diolah lebih lanjut di Excel atau alat analisis lain.
- **Export Excel** — mengunduh rekapitulasi dalam format `.xlsx` siap pakai, termasuk seluruh seksi.

### Yang Harus Dilakukan Admin Secara Manual (Belum Otomatis di Sistem)
Untuk kebutuhan pelaporan resmi ke Kanwil/Pusat yang memerlukan format PDF cetak atau kompilasi bukti pendukung dalam satu arsip, lakukan langkah berikut sebagai solusi sementara:

- **Untuk laporan cetak (PDF)**: unduh hasil Export Excel, lalu gunakan fitur "Save as PDF" / "Print to PDF" dari aplikasi spreadsheet (Excel, Google Sheets, atau LibreOffice Calc) untuk menghasilkan versi PDF yang rapi dan siap cetak.
- **Untuk kompilasi bukti pendukung (ZIP)**: unduh dokumen pendukung satu per satu dari setiap assessment yang dibutuhkan, kumpulkan dalam satu folder lokal, lalu kompres folder tersebut menjadi `.zip` menggunakan aplikasi kompresi standar (Windows: klik kanan → "Send to" → "Compressed folder"; Mac: klik kanan → "Compress").

**Catatan untuk pengembangan sistem ke depan**: fitur Export PDF langsung dari sistem dan Download Semua Bukti (ZIP) otomatis belum tersedia di versi ini. Sampaikan kebutuhan ini ke tim developer jika proses manual di atas dirasa terlalu memberatkan beban kerja rutin Anda.

---

## 5. Monitoring Dashboard (Lintas Seksi)

Berbeda dengan user biasa yang hanya melihat ringkasan seksinya sendiri, Admin dapat melihat profil risiko seluruh unit KPPN.

1. Buka halaman **Dashboard**.
2. Anda akan melihat angka agregat dari seluruh 25 indikator aktif di KPPN, bukan hanya seksi tertentu.
3. Tabel **Daftar Indikator Risiko** menampilkan kode, nama, dan PIC Utama setiap indikator — gunakan ini untuk mengetahui dengan cepat seksi mana yang bertanggung jawab atas indikator tertentu.
4. Untuk 4 **Indikator Bersama** (RE#2.3, RE#3.3, RE#5.1, RE#6.1), perhatikan bahwa hanya PIC Utama yang dapat mengisi data — PIC Pendamping hanya dapat melihat. Pastikan PIC Utama dari masing-masing indikator bersama ini benar-benar mengisi datanya setiap quarter.

---

## 6. Audit Log (Jejak Rekam)

Jika terjadi perubahan data yang mencurigakan atau Anda perlu menelusuri riwayat aktivitas pengguna, seluruh aksi penting (login, logout, register user baru, reset password, ganti password, dll) tercatat secara otomatis di tabel `audit_logs`.

Untuk melihat audit log saat ini, hubungi tim teknis/developer untuk melakukan query langsung ke database Supabase, karena belum ada tampilan UI khusus untuk membaca audit log di dalam aplikasi pada versi ini.

---

## 7. Backup & Restore Database

Karena aplikasi ini terhubung dengan layanan cloud Supabase, backup berjalan otomatis di sisi Supabase. Namun, sebagai langkah pengamanan tambahan yang sangat disarankan, Admin sebaiknya melakukan Export Manual secara berkala (disarankan setiap akhir kuartal, bertepatan dengan siklus Kirim Final):

1. Login ke Dashboard Supabase milik KPPN.
2. Masuk ke menu **Database** → **Backups**.
3. Klik **Download** untuk menyimpan file SQL dump sebagai arsip luring (offline) di server lokal atau komputer KPPN.
4. Simpan file backup dengan format nama yang jelas, contoh: `backup_risiko_Q1_2026.sql`, agar mudah ditemukan saat dibutuhkan kembali.

---

## Ringkasan Tugas Rutin Admin per Quarter

| Tugas | Kapan Dilakukan |
|---|---|
| Pantau progres pengisian tiap seksi | Sepanjang periode quarter berjalan |
| Tagih seksi yang belum submit | Mendekati tanggal pengunci quarter |
| Tinjau kewajaran data setelah Submitted | Setelah seksi melakukan Batch Submit |
| Reset password pegawai yang lupa | Sesuai kebutuhan/permintaan |
| Tambah/kelola akun user | Saat ada pegawai baru/mutasi |
| Export laporan untuk Kanwil/Pusat | Setelah quarter ditutup |
| Backup manual database | Disarankan setiap akhir quarter |

---

**Butuh bantuan teknis lebih lanjut?**
Hubungi tim developer/teknis untuk permintaan yang memerlukan akses langsung ke database atau pengembangan fitur yang belum tersedia di versi ini.