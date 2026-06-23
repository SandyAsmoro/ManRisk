# 📖 Panduan Pengguna - Sistem Manajemen Risiko KPPN

## Daftar Isi
1. [Login](#login)
2. [Lupa Password](#lupa-password)
3. [Dashboard](#dashboard)
4. [Input Data Risiko](#input-data-risiko)
5. [Kirim Final (Batch Submit)](#kirim-final-batch-submit)
6. [Laporan & Rekap](#laporan--rekap)
7. [FAQ](#faq)

## Login

1. Buka halaman login aplikasi.
2. Masukkan **username** dan **password**.
3. Klik **"Login"**.
4. Anda akan diarahkan ke Dashboard.

Jika password Anda baru saja direset oleh Admin, sistem akan otomatis mengarahkan Anda ke halaman **Ganti Password** sebelum Anda bisa mengakses halaman lain. Anda wajib membuat password baru sebelum melanjutkan.

## Lupa Password

Sistem ini **tidak menggunakan reset password via email**. Jika Anda lupa password:

1. Hubungi **Admin** Anda secara langsung (telepon/WhatsApp/tatap muka).
2. Admin akan mereset password Anda dan memberikan **password sementara**.
3. Login menggunakan password sementara tersebut.
4. Sistem akan otomatis mengarahkan Anda ke halaman **Ganti Password** — Anda tidak bisa mengakses halaman lain sebelum membuat password baru.
5. Buat password baru, lalu Anda bisa menggunakan sistem secara normal.

**Catatan:** simpan password baru Anda baik-baik. Password sementara dari Admin hanya berlaku satu kali pakai.

## Dashboard

Dashboard adalah halaman utama setelah Anda login. Di sinilah Anda memantau ringkasan risiko dan melihat seluruh indikator yang ada.

### Tampilan Utama
- **Pilihan Periode**: Dropdown di kanan atas untuk memilih Quarter 1–4. Pilihan ini memuat ulang ringkasan risiko sesuai quarter yang dipilih.
- **Kartu Ringkasan Kategori Warna**: 5 kartu berwarna (Biru, Hijau, Kuning, Jingga, Merah) menampilkan jumlah indikator pada masing-masing kategori risiko untuk quarter yang dipilih.
- **Matriks Risiko Visual**: Visualisasi matriks 5×5 sesuai standar Kementerian Keuangan.
- **Daftar Indikator Risiko**: Tabel berisi seluruh 25 indikator aktif, lengkap dengan kode, nama indikator, dan PIC Utama masing-masing.

Dashboard memperbarui data **secara otomatis setiap 30 detik** tanpa perlu Anda refresh halaman manual — ditandai dengan indikator titik hijau berkedip di sebelah judul.

**Catatan tentang riwayat & tracking P26/R26**: Untuk melihat riwayat perubahan nilai risiko antar quarter (Q1→Q2→Q3→Q4) atau perbandingan terhadap P26/R26, silakan hubungi Admin untuk menarik data riwayat tersebut melalui Laporan, karena versi sistem saat ini belum menyediakan tampilan grafik tracking otomatis di Dashboard.

### Menu Navigasi (Sidebar)
- **Dashboard** — ringkasan risiko & daftar indikator (halaman ini)
- **Input Data Risiko** — isi data Frekuensi/Dampak per indikator
- **Laporan & Rekap** — unduh rekapitulasi data dalam format Excel/CSV

Menu **Tambah User** dan **Kelola User** hanya muncul jika Anda login sebagai **Admin**.

## Input Data Risiko

Buka menu **Input Data Risiko** di sidebar.

### Catatan Jadwal Pengisian (Quarter Locking)

Sistem menggunakan jadwal kuartal kalender standar. Form input hanya aktif sesuai bulan berjalan:

| Quarter | Periode Bulan | Dibuka | Dikunci Otomatis |
|---|---|---|---|
| Q1 | Januari–Maret | 1 Januari | 31 Maret, 23:59 |
| Q2 | April–Juni | 1 April | 30 Juni, 23:59 |
| Q3 | Juli–September | 1 Juli | 30 September, 23:59 |
| Q4 | Oktober–Desember | 1 Oktober | 31 Desember, 23:59 |

**Catatan**: Admin memiliki hak akses istimewa untuk melakukan koreksi data di luar jadwal ini jika diperlukan.

### Langkah Pengisian

**1. Pilih Indikator Risiko**
Pilih dari dropdown indikator yang tersedia. Jika indikator yang Anda pilih memiliki lebih dari satu PIC, akan muncul badge ungu **"🤝 Indikator Bersama"** yang menunjukkan siapa PIC Utama (Primary) dan siapa PIC Pendamping (Secondary).

> **Jika Anda adalah PIC Pendamping** untuk indikator tertentu, form akan otomatis terkunci (mode **Hanya Baca**) dengan keterangan "Pengisian data hanya dapat dilakukan oleh [PIC Utama]". Ini berlaku untuk 4 indikator bersama dalam sistem.

**2. Pilih Quarter**
Pilih periode quarter yang ingin diisi (Q1–Q4).

**3. Isi Frekuensi dan Dampak (Skala 1–5)**

*Frekuensi Kejadian:*
```
1 = Jarang (< 1x setahun)
2 = Jarang (1-3x setahun)
3 = Sedang (4-6x setahun)
4 = Sering (7-12x setahun)
5 = Sangat Sering (> 12x setahun)
```

*Dampak/Besaran Risiko:*
```
1 = Minimal (Kerugian < Rp 10 juta)
2 = Rendah (Kerugian Rp 10-100 juta)
3 = Sedang (Kerugian Rp 100 juta - 1 miliar)
4 = Tinggi (Kerugian Rp 1-10 miliar)
5 = Sangat Tinggi (Kerugian > Rp 10 miliar)
```

Sistem otomatis menghitung Nilai Risiko dan kategori warnanya berdasarkan **Matriks Resmi Kementerian Keuangan (Pola 5x5)** — bukan sekadar perkalian sederhana. Setiap kombinasi Frekuensi × Dampak punya kategori warna yang sudah ditetapkan secara resmi:

```
🟦 BIRU:    Risiko Rendah
🟩 HIJAU:   Risiko Sedang Rendah
🟨 KUNING:  Risiko Sedang
🟧 JINGGA:  Risiko Tinggi
🟥 MERAH:   Risiko Sangat Tinggi
```

**4. Isi Tindakan Mitigasi (Opsional)**
Kolom teks bebas untuk mencatat langkah mitigasi yang sudah/akan dilakukan.

**5. Upload Bukti Pendukung (Opsional)**
```
Format yang diizinkan: PDF, JPG, PNG, ZIP
Ukuran maksimal: 5 MB per file
```
Sistem memvalidasi isi file (bukan hanya ekstensi nama file) untuk memastikan file yang diupload benar-benar sesuai jenisnya. File yang tidak sesuai akan ditolak otomatis.

**6. Simpan Data (Draf)**
Klik tombol **"Simpan Data (Draf)"**. Data tersimpan dengan status **Draft** dan masih bisa diedit/diubah.

> **Mode offline**: Jika koneksi internet Anda terputus saat mengisi form, sistem akan menampilkan peringatan dan menyimpan ketikan Anda sementara di browser (Local Storage) agar tidak hilang. Saat Anda kembali memilih indikator dan quarter yang sama, sistem akan menawarkan untuk memuat ulang draft tersebut.

## Kirim Final (Batch Submit)

Berbeda dari versi sebelumnya, Anda **tidak perlu submit satu per satu** untuk setiap indikator. Setelah seluruh 25 indikator untuk quarter tertentu sudah diisi (statusnya Draft), gunakan panel **"Kirim Dokumen Final Kuartal"** di bagian bawah halaman Input Data:

1. Pilih **Quarter** dan **Tahun** yang ingin dikirim final.
2. Klik **"Kirim Final (Batch Submit)"**.
3. Sistem akan memeriksa apakah seluruh 25 indikator untuk seksi Anda sudah terisi.
   - Jika **ada yang belum diisi**, sistem menampilkan daftar lengkap indikator yang masih kosong — lengkapi dahulu sebelum mencoba kirim final lagi.
   - Jika **semua sudah lengkap**, seluruh data akan berubah status menjadi **Submitted** dan **terkunci permanen** — tidak bisa diedit lagi setelah ini.

**Peringatan**: Pastikan semua data benar sebelum Kirim Final, karena data yang sudah berstatus Submitted tidak dapat diubah kembali oleh user biasa. Jika ada kesalahan setelah submit, hubungi Admin.

## Laporan & Rekap

Buka menu **Laporan & Rekap** di sidebar untuk mengunduh rekapitulasi data risiko.

Tombol yang tersedia:
- **Export CSV** — unduh data dalam format CSV
- **Export Excel** — unduh data dalam format Excel (.xlsx)

## FAQ

### Q: Kapan saya bisa mengisi data Q2?
A: Q2 hanya bisa diisi pada bulan April–Juni. Di luar bulan tersebut, form akan ditolak sistem (kecuali Anda Admin).

### Q: Apakah saya bisa edit data setelah Kirim Final?
A: Tidak. Setelah status berubah menjadi "Submitted", data terkunci permanen untuk user biasa. Hubungi Admin jika perlu koreksi.

### Q: Bagaimana jika lupa upload bukti pendukung?
A: Bukti pendukung di versi ini bersifat **opsional**, bukan wajib — Anda tetap bisa menyimpan data draft tanpa lampiran.

### Q: Berapa ukuran file maksimal yang bisa diupload?
A: Maksimal **5 MB** per file. Format yang didukung: PDF, JPG, PNG, ZIP.

### Q: Saya lupa password, bagaimana cara reset?
A: Sistem ini tidak punya fitur reset mandiri via email. Hubungi Admin untuk meminta password sementara, lalu Anda akan diminta membuat password baru saat login pertama.

### Q: Apa itu "Indikator Bersama"?
A: Beberapa indikator memiliki dua PIC — Primary (yang mengisi data) dan Secondary (yang hanya bisa melihat). Badge ungu "🤝 Indikator Bersama" akan muncul pada indikator tersebut.

### Q: Siapa yang bisa lihat data risiko saya?
A: Admin dapat melihat seluruh data semua seksi. User biasa hanya dapat melihat data seksinya sendiri (dan data Indikator Bersama yang melibatkan seksinya sebagai PIC Pendamping).

### Q: Kenapa data di Dashboard berubah sendiri tanpa saya refresh?
A: Dashboard memuat ulang data otomatis setiap 30 detik agar selalu menampilkan informasi terbaru.

---

**Butuh bantuan?**
Hubungi Admin sistem Anda secara langsung untuk masalah teknis, lupa password, atau permintaan koreksi data.