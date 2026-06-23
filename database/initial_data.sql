-- =========================================================
-- Risk Matrix Mapping (Standar Warna - Pola 5x5)
-- Sumber: Matriks Analisis Risiko Organisasi, Kementerian Keuangan RI
-- frequency = Tingkat Frekuensi (1-5), impact = Tingkat Dampak (1-5)
-- risk_value = posisi nilai pada matriks (bukan frequency * impact)
-- =========================================================
INSERT INTO risk_matrix_mapping (risk_value, frequency, impact, category, color_code, description, mitigation_level) VALUES
-- Biru: Risiko Rendah
(1, 1, 1, 'Biru', '#0066CC', 'Risiko Rendah', 'Low'),
(2, 2, 1, 'Biru', '#0066CC', 'Risiko Rendah', 'Low'),
(3, 1, 2, 'Biru', '#0066CC', 'Risiko Rendah', 'Low'),
(4, 3, 1, 'Biru', '#0066CC', 'Risiko Rendah', 'Low'),
(5, 1, 3, 'Biru', '#0066CC', 'Risiko Rendah', 'Low'),
-- Hijau Tua: Risiko Sedang-Rendah
(6, 4, 1, 'Hijau Tua', '#006600', 'Risiko Sedang-Rendah', 'Low-Medium'),
(7, 2, 2, 'Hijau Tua', '#006600', 'Risiko Sedang-Rendah', 'Low-Medium'),
(8, 1, 4, 'Hijau Tua', '#006600', 'Risiko Sedang-Rendah', 'Low-Medium'),
(9, 5, 1, 'Hijau Tua', '#006600', 'Risiko Sedang-Rendah', 'Low-Medium'),
(10, 3, 2, 'Hijau Tua', '#006600', 'Risiko Sedang-Rendah', 'Low-Medium'),
(11, 2, 3, 'Hijau Tua', '#006600', 'Risiko Sedang-Rendah', 'Low-Medium'),
-- Kuning: Risiko Sedang
(12, 4, 2, 'Kuning', '#FFFF00', 'Risiko Sedang', 'Medium'),
(13, 2, 4, 'Kuning', '#FFFF00', 'Risiko Sedang', 'Medium'),
(14, 3, 3, 'Kuning', '#FFFF00', 'Risiko Sedang', 'Medium'),
(15, 5, 2, 'Kuning', '#FFFF00', 'Risiko Sedang', 'Medium'),
-- Oranye: Risiko Tinggi
(16, 4, 3, 'Oranye', '#FF9900', 'Risiko Tinggi', 'High'),
(17, 3, 4, 'Oranye', '#FF9900', 'Risiko Tinggi', 'High'),
(18, 5, 3, 'Oranye', '#FF9900', 'Risiko Tinggi', 'High'),
(19, 4, 4, 'Oranye', '#FF9900', 'Risiko Tinggi', 'High'),
-- Merah: Risiko Sangat Tinggi
(20, 1, 5, 'Merah', '#FF0000', 'Risiko Sangat Tinggi', 'Critical'),
(21, 2, 5, 'Merah', '#FF0000', 'Risiko Sangat Tinggi', 'Critical'),
(22, 3, 5, 'Merah', '#FF0000', 'Risiko Sangat Tinggi', 'Critical'),
(23, 5, 4, 'Merah', '#FF0000', 'Risiko Sangat Tinggi', 'Critical'),
(24, 4, 5, 'Merah', '#FF0000', 'Risiko Sangat Tinggi', 'Critical'),
(25, 5, 5, 'Merah', '#FF0000', 'Risiko Sangat Tinggi', 'Critical');

-- =========================================================
-- Risk Indicators (28 indikator)
-- Sumber: Mitigasi_Risiko.xlsx
-- p26_initial = kolom P26, r26_target = kolom R26
-- =========================================================
INSERT INTO risk_indicators (indicator_code, indicator_name, indicator_description, indicator_type, pic_section, p26_initial, r26_target, effective_quarter, effective_year) VALUES
('1a-CP-RE#1.1', 'Nilai Kinerja Pelaksanaan Anggaran K/L', 'Satker tidak valid dalam mengisi capaian output', 'IKU', 'Seksi MSKI', 14, 10, 'Q1', 2024),
('1a-CP-RE#1.2', 'Nilai Kinerja Pelaksanaan Anggaran K/L', 'Rendahnya nilai kualitas pelaksanaan anggaran', 'IKU', 'Seksi MSKI', 19, 16, 'Q1', 2024),
('1a-CP-RE#1.3', 'Nilai Kinerja Pelaksanaan Anggaran K/L', 'Satker terlambat menyampaikan pertanggungjawaban UP/TUP', 'IKU', 'Seksi MSKI', 19, 15, 'Q1', 2024),
('2a-CP-RE#2.1', 'Indeks Kepuasan terhadap Layanan KPPN', 'Edukasi dan komunikasi yang tidak optimal', 'IKU', 'Seksi MSKI', 13, 10, 'Q1', 2024),
('2a-CP-RE#2.3', 'Indeks Kepuasan terhadap Layanan KPPN', 'Respon atas pertanyaan/konsultasi dari pengguna layanan tidak tepat waktu', 'IKU', 'Seksi MSKI,Subbagian Umum', 16, 15, 'Q1', 2024),
('2b-N-01', 'Tingkat Implementasi Penajaman Tugas Financial Advisory', '', 'Non-IKU', 'Seksi MSKI', NULL, NULL, 'Q1', 2024),
('3a-CP-RE#3.1', 'Indeks Kinerja Penyaluran Dana Transfer ke Daerah pada KPPN', 'TKD tidak disalurkan tepat waktu', 'IKU', 'Seksi Bank', 16, 15, 'Q1', 2024),
('3b-N-RE#3.3', 'Indeks Kualitas Penyelesaian SP2D dan Akurasi Perencanaan Kas', 'Waktu pengajuan SPM tidak sesuai RPD', 'Non-IKU', 'Seksi MSKI,Seksi PD', 17, 13, 'Q1', 2024),
('3b-N-RE#3.4', 'Indeks Kualitas Penyelesaian SP2D dan Akurasi Perencanaan Kas', 'Penyelesaian SP2D lebih dari 1 (satu) jam', 'Non-IKU', 'Seksi PD', 17, 13, 'Q1', 2024),
('3b-N-RE#3.6', 'Indeks Kualitas Penyelesaian SP2D dan Akurasi Perencanaan Kas', 'Bertambahnya jumlah retur', 'Non-IKU', 'Seksi PD', 22, 16, 'Q1', 2024),
('3b-N-RE#3.7', 'Indeks Kualitas Penyelesaian SP2D dan Akurasi Perencanaan Kas', 'Penyelesaian retur tidak tepat waktu', 'Non-IKU', 'Seksi Vera', 14, 10, 'Q1', 2024),
('3c-N-01', 'Indeks Digitalisasi Pengelolaan Keuangan', '', 'Non-IKU', 'Seksi MSKI', NULL, NULL, 'Q1', 2024),
('4a-N-RE#4.1', 'Indeks Akuntabilitas Pelaporan Keuangan Satker', 'Keterlambatan LPJ bendahara oleh bendahara K/L', 'IKU', 'Seksi Vera', 16, 15, 'Q1', 2024),
('4a-N-RE#4.2', 'Indeks Akuntabilitas Pelaporan Keuangan Satker', 'Terdapat satuan kerja yang terlambat tutup periode permanen', 'IKU', 'Seksi Vera', 16, 15, 'Q1', 2024),
('5a-N-RE#5.4', 'Tingkat Kualitas Pengelolaan Kinerja Organisasi', 'Kurang optimalnya pimpinan unit dalam mengimplementasikan prinsip-prinsip SFO', 'Non-IKU', 'Subbagian Umum', 17, 10, 'Q1', 2024),
('5b-N-01', 'Nilai Kualitas Pengelolaan SDM', '', 'Non-IKU', 'Subbagian Umum', NULL, NULL, 'Q1', 2024),
('5c-N-01', 'Nilai Hasil Evaluasi Pelaksanaan Tugas Kepatuhan Internal', '', 'Non-IKU', 'Subbagian Umum', NULL, NULL, 'Q1', 2024),
('6a-CP-RE#6.3', 'Indeks Kualitas Pengelolaan Keuangan, BMN, Pengadaan, dan Arsip', 'Kualitas LK tingkat UAKPA dan UAKPB tidak maksimal', 'IKU', 'Subbagian Umum', 17, 10, 'Q1', 2024),
('6a-CP-RE#6.4', 'Indeks Kualitas Pengelolaan Keuangan, BMN, Pengadaan, dan Arsip', 'Kebakaran gedung kantor', 'IKU', 'Subbagian Umum', 16, 15, 'Q1', 2024),
('6a-CP-RE#6.5', 'Indeks Kualitas Pengelolaan Keuangan, BMN, Pengadaan, dan Arsip', 'Penerapan gedung ramah lingkungan', 'IKU', 'Subbagian Umum', 13, 17, 'Q1', 2024),
('6a-CP-RE#6.6', 'Indeks Kualitas Pengelolaan Keuangan, BMN, Pengadaan, dan Arsip', 'Kerusakan BMN', 'IKU', 'Subbagian Umum', 14, 11, 'Q1', 2024),
('6b-N-RE#6.7', 'Nilai Kinerja TIK Kanwil DJPb', 'Penyalahgunaan user aplikasi KemenKeu oleh pihak yang tidak berwenang', 'Non-IKU', 'Subbagian Umum', 13, 10, 'Q1', 2024),
('NON-IKU-RE#6.2', 'Penguatan fungsi kehumasan media dan kehumasan lembaga KPPN sebagai financial advisory', '', 'Non-IKU', 'Subbagian Umum', 17, 22, 'Q1', 2024),
('NON-IKU-RE#2.2', 'Penggunaan website kantor sebagai media penyebarluasan informasi', '', 'Non-IKU', 'Subbagian Umum', 16, 22, 'Q1', 2024),
('NON-IKU-RE#3.2', 'Potensi moral hazard oleh satker pada aplikasi gaji dan tukin', '', 'Non-IKU', 'Seksi MSKI', 19, 15, 'Q1', 2024),
('MANDATORY-RE#5.1', 'Persepsi negatif masyarakat atas pemberitaan di media massa dan media sosial', '', 'Mandatory', 'Subbagian Umum,Seksi MSKI', 22, 15, 'Q1', 2024),
('MANDATORY-RE#5.2', 'Ownership pegawai terhadap organisasi', '', 'Mandatory', 'Seksi MSKI', 22, 15, 'Q1', 2024),
('MANDATORY-RE#5.3', 'Adanya perilaku korupsi pada pegawai', '', 'Mandatory', 'Seksi MSKI', 16, 15, 'Q1', 2024),
('MANDATORY-RE#6.1', 'Kebocoran data dan informasi terkait konfidensial/rahasia', '', 'Mandatory', 'Subbagian Umum,Seksi MSKI', 16, 15, 'Q1', 2024);
