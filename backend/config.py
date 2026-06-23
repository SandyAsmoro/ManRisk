import datetime

# Aturan Penguncian Kuartal (Quarter Locking)
QUARTER_EDIT_WINDOWS = {
    # Q1 = Januari–Maret    → input dibuka 1 Jan,  ditutup 31 Mar
    'Q1': {'months': [1, 2, 3],    'lock_end_month': 3,  'lock_end_day': 31},
    # Q2 = April–Juni       → input dibuka 1 Apr,  ditutup 30 Jun
    'Q2': {'months': [4, 5, 6],    'lock_end_month': 6,  'lock_end_day': 30},
    # Q3 = Juli–September   → input dibuka 1 Jul,  ditutup 30 Sep
    'Q3': {'months': [7, 8, 9],    'lock_end_month': 9,  'lock_end_day': 30},
    # Q4 = Oktober–Desember → input dibuka 1 Okt,  ditutup 31 Des
    'Q4': {'months': [10, 11, 12], 'lock_end_month': 12, 'lock_end_day': 31},
}

def is_editable(quarter, year=None, current_date=None):
    """
    Mengecek apakah suatu data asesmen boleh di-create/update.
    """
    if current_date is None:
        current_date = datetime.datetime.now()
        
    # Validasi Tahun (Tolak jika mencoba mengedit data tahun lalu)
    if year and int(year) != current_date.year:
        return False
        
    allowed_months = QUARTER_EDIT_WINDOWS.get(quarter, {}).get('months', [])
    return current_date.month in allowed_months