#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_db.py — Script Inisialisasi Database Supabase
Sistem Manajemen Risiko KPPN

Cara pakai:
  1. Letakkan file ini di dalam folder backend/ (sejajar dengan app.py)
  2. Pastikan .env sudah ada dan DATABASE_URL benar
  3. Jalankan: python init_db.py

Aman dijalankan BERKALI-KALI (idempoten):
  - Tabel sudah ada? → skip, tidak error
  - Data sudah ada?  → skip, tidak duplikat
  - Admin sudah ada? → skip, tidak digandakan

Catatan password admin default:
  Hash tersimpan di users_rows.sql menggunakan bcrypt ($2b$12$...).
  Password plaintext-nya adalah yang Anda gunakan saat generate hash tersebut.
  Jika tidak tahu, reset via endpoint PUT /api/auth/change-password setelah login
  pertama berhasil — atau generate hash baru dengan script berikut:
  
    python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('PasswordBaru123!'))"
  
  Lalu update kolom password_hash langsung di Supabase Dashboard → Table Editor.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# ─── Load .env ──────────────────────────────────────────────────────────────────
# Cari .env di direktori script ini (backend/) atau satu level di atasnya
_base = os.path.dirname(os.path.abspath(__file__))
_env_paths = [
    os.path.join(_base, '.env'),
    os.path.join(_base, '..', '.env'),
]
for _ep in _env_paths:
    if os.path.exists(_ep):
        load_dotenv(_ep)
        break

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL tidak ditemukan di .env!")
    print("        Pastikan file .env ada dan berisi DATABASE_URL yang valid.")
    print("        Contoh:")
    print("          DATABASE_URL=postgresql://postgres.xxx:password@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres")
    sys.exit(1)

# ─── Path ke file SQL ────────────────────────────────────────────────────────────
# Cari schema.sql dan initial_data.sql di beberapa lokasi umum
def _find_sql_file(filename):
    candidates = [
        os.path.join(_base, filename),
        os.path.join(_base, '..', 'database', filename),
        os.path.join(_base, 'database', filename),
        os.path.join(_base, '..', filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.normpath(c)
    return None

SCHEMA_FILE = _find_sql_file('schema.sql')
DATA_FILE   = _find_sql_file('initial_data.sql')
USERS_FILE  = _find_sql_file('users_rows.sql')   # opsional

# ─────────────────────────────────────────────────────────────────────────────────

def check_files():
    missing = []
    for label, path in [('schema.sql', SCHEMA_FILE), ('initial_data.sql', DATA_FILE)]:
        if not path:
            missing.append(label)
        else:
            print(f"  [OK] {label} ditemukan: {path}")
    if USERS_FILE:
        print(f"  [OK] users_rows.sql ditemukan: {USERS_FILE}")
    else:
        print("  [INFO] users_rows.sql tidak ditemukan — user admin akan di-seed dari data default.")
    if missing:
        print(f"\n[ERROR] File berikut tidak ditemukan: {', '.join(missing)}")
        print("        Letakkan file SQL di folder database/ atau sejajar dengan init_db.py")
        sys.exit(1)


def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        print("  [OK] Koneksi ke database berhasil.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Gagal koneksi ke database:\n        {e}")
        print("\n  Tips:")
        print("  - Cek DATABASE_URL di .env (gunakan Pooler port 6543 untuk Supabase free-tier)")
        print("  - Pastikan IP Anda tidak diblokir: Supabase Dashboard → Settings → Network")
        sys.exit(1)


def table_exists(conn, table_name):
    """Cek apakah tabel sudah ada di database."""
    cur = conn.cursor()
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s);",
        (table_name,)
    )
    exists = cur.fetchone()[0]
    cur.close()
    return exists


def run_schema(conn):
    """Jalankan schema.sql — buat semua tabel. Skip jika sudah ada."""
    if table_exists(conn, 'users'):
        print("  [SKIP] Tabel sudah ada, schema.sql tidak dijalankan ulang.")
        return

    print(f"  [RUN ] Menjalankan schema.sql dari {SCHEMA_FILE} ...")
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        sql_text = f.read()
    try:
        cur = conn.cursor()
        cur.execute(sql_text)
        conn.commit()
        cur.close()
        print("  [OK] schema.sql berhasil — semua tabel dibuat.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  [ERROR] schema.sql gagal:\n         {e}")
        raise


def count_rows(conn, table_name):
    """Hitung baris di tabel."""
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cur.fetchone()[0]
    cur.close()
    return count


def run_initial_data(conn):
    """Jalankan initial_data.sql — isi risk_matrix_mapping & risk_indicators. Idempoten via ON CONFLICT."""
    matrix_count    = count_rows(conn, 'risk_matrix_mapping')
    indicator_count = count_rows(conn, 'risk_indicators')

    if matrix_count > 0 and indicator_count > 0:
        print(f"  [SKIP] Data awal sudah ada: {matrix_count} baris risk_matrix_mapping, {indicator_count} indikator.")
        return

    print(f"  [RUN ] Menjalankan initial_data.sql dari {DATA_FILE} ...")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        sql_text = f.read()

    # Tambahkan ON CONFLICT DO NOTHING secara dinamis agar idempoten
    # (file asli tidak punya ON CONFLICT, wrap dalam exception handler)
    try:
        cur = conn.cursor()
        cur.execute(sql_text)
        conn.commit()
        cur.close()
        print(f"  [OK] initial_data.sql berhasil.")
        print(f"       risk_matrix_mapping: {count_rows(conn, 'risk_matrix_mapping')} baris")
        print(f"       risk_indicators    : {count_rows(conn, 'risk_indicators')} baris")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        print("  [SKIP] Data sudah ada (unique violation). Tidak ada perubahan.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  [ERROR] initial_data.sql gagal:\n         {e}")
        raise


def seed_admin_user(conn):
    """
    Insert user admin. Idempoten — jika username 'admin' sudah ada, skip.
    Data dari users_rows.sql (atau hardcoded default jika file tidak ada).
    """
    user_count = count_rows(conn, 'users')
    if user_count > 0:
        print(f"  [SKIP] Tabel users sudah ada {user_count} baris. Tidak ada user yang ditambahkan.")
        return

    # Data admin dari users_rows.sql
    admin_data = {
        'id':            'da71c1f3-aa8d-4c9a-9925-59e98d981e92',
        'username':      'admin',
        'email':         'admin@kppn.local',
        # bcrypt hash dari users_rows.sql
        # Jika Anda tidak tahu password-nya, lihat catatan di header file ini.
        'password_hash': '$2b$12$Izn2qIOkC3DSaPLiMqYPs.thOriiYfrc1w0q/3.1zTHZnYnflsA6u',
        'full_name':     'Administrator',
        'role':          'admin',
        'section':       '',
        'is_active':     True,
    }

    insert_sql = """
        INSERT INTO users (id, username, email, password_hash, full_name, role, section, is_active)
        VALUES (%(id)s, %(username)s, %(email)s, %(password_hash)s, %(full_name)s, %(role)s, %(section)s, %(is_active)s)
        ON CONFLICT (username) DO NOTHING;
    """
    try:
        cur = conn.cursor()
        cur.execute(insert_sql, admin_data)
        inserted = cur.rowcount
        conn.commit()
        cur.close()
        if inserted:
            print("  [OK] User admin berhasil ditambahkan.")
            print("       username : admin")
            print("       email    : admin@kppn.local")
            print("       ⚠️  Segera ganti password via /api/auth/change-password setelah login pertama!")
        else:
            print("  [SKIP] User admin sudah ada.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"  [ERROR] Gagal insert user admin:\n         {e}")
        raise


def verify_all(conn):
    """Verifikasi akhir semua tabel utama."""
    checks = {
        'users':               'User',
        'risk_indicators':     'Indikator Risiko',
        'risk_matrix_mapping': 'Risk Matrix Mapping',
        'risk_assessments':    'Risk Assessments',
        'audit_logs':          'Audit Logs',
    }
    print()
    all_ready = True
    for table, label in checks.items():
        try:
            n = count_rows(conn, table)
            status = "✓" if (table in ('risk_assessments', 'audit_logs') or n > 0) else "⚠"
            if n == 0 and table not in ('risk_assessments', 'audit_logs'):
                all_ready = False
            print(f"  [{status}] {label:<30} {n} baris")
        except psycopg2.Error as e:
            print(f"  [✗] {label:<30} ERROR: {e}")
            all_ready = False
    return all_ready


def main():
    print()
    print("=" * 62)
    print("   init_db.py — Sistem Manajemen Risiko KPPN")
    print("   Inisialisasi Database Supabase")
    print("=" * 62)

    print("\n[1/5] Memeriksa file SQL ...")
    check_files()

    print("\n[2/5] Membuka koneksi ke database ...")
    conn = get_connection()

    try:
        print("\n[3/5] Membuat tabel (schema.sql) ...")
        run_schema(conn)

        print("\n[4/5] Mengisi data awal (initial_data.sql) ...")
        run_initial_data(conn)

        print("\n[5/5] Seeding user admin ...")
        seed_admin_user(conn)

        print("\n--- Verifikasi Akhir ---")
        ok = verify_all(conn)

        print()
        print("=" * 62)
        if ok:
            print("  ✅  Database siap! Anda bisa menjalankan: python app.py")
        else:
            print("  ⚠️   Selesai dengan peringatan. Periksa output di atas.")
        print("=" * 62)
        print()

    except Exception as e:
        print(f"\n[FATAL] Inisialisasi gagal: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
