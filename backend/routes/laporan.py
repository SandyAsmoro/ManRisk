import os
import io
import json
import zipfile
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import SupportingDocument, RiskAssessment, RiskIndicator, User
import pandas as pd
from fpdf import FPDF

# === IMPORT TAMBAHAN UNTUK GOOGLE DRIVE ===
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

laporan_bp = Blueprint('laporan', __name__)

# =====================================================================
# 1. INISIALISASI DUAL-STORAGE (SUPABASE & GOOGLE DRIVE)
# =====================================================================
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase_client = None
if supabase_url and supabase_key:
    from supabase import create_client
    supabase_client = create_client(supabase_url, supabase_key)

SCOPES = ['https://www.googleapis.com/auth/drive']
GOOGLE_CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS_JSON')
creds = None
drive_service = None

if GOOGLE_CREDENTIALS_JSON:
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Gagal memuat kredensial Google Drive: {e}")

# =====================================================================
# FUNGSI HELPER: TARIK DATA DATABASE UNTUK EKSPOR TABEL
# =====================================================================
def get_export_data(quarter, year, user):
    """Helper untuk menarik data dari database berdasarkan filter"""
    query = db.session.query(RiskAssessment, RiskIndicator).join(RiskIndicator).filter(RiskAssessment.status == 'verified')
    
    if user.role != 'admin':
        query = query.filter(RiskAssessment.section == user.section)
        
    if quarter:
        query = query.filter(RiskAssessment.quarter == quarter)
    if year:
        query = query.filter(RiskAssessment.year == int(year))
        
    assessments = query.all()
    data = []
    for ass, ind in assessments:
        data.append({
            'Kode IKU': ind.indicator_code,
            'PIC': ass.section,
            'IRU': ind.name,
            'Kejadian Risiko': ind.risk_event,
            'P26': ass.p26_score,
            'R26': ass.r26_score,
            'Triwulan Sebelumnya': ass.previous_quarter_score or '-',
            'Triwulan': ass.quarter,
            'Skor Risiko (Current)': ass.risk_value,
            'Alasan Perubahan Risiko': ass.change_reason or '-'
        })
    return data

# ==========================================
# 2. ENDPOINT EXPORT DATA (CSV, EXCEL, PDF)
# ==========================================
@laporan_bp.route('/export', methods=['GET'])
@jwt_required()
def export_data():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    export_type = request.args.get('type', 'csv').lower()
    quarter = request.args.get('quarter', '')
    year = request.args.get('year', datetime.now().year)
    
    data = get_export_data(quarter, year, user)
    if not data:
        return jsonify({'status': 'error', 'message': 'Tidak ada data terverifikasi (disetujui Admin) pada periode tersebut untuk diekspor.'}), 404
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"Laporan_Risiko_{quarter or 'Semua_Q'}_{year}"
    
    # --- 1. EXPORT CSV ---
    if export_type == 'csv':
        df = pd.DataFrame(data)
        csv_data = df.to_csv(index=False, sep=';')
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = f"attachment; filename={filename_base}.csv"
        response.headers["Content-type"] = "text/csv"
        return response
        
    # --- 2. EXPORT EXCEL ---
    elif export_type == 'excel':
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data Risiko')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'{filename_base}.xlsx')
        
    # --- 3. EXPORT PDF DENGAN MULTILINE TEXT (WRAPPING) ---
    elif export_type == 'pdf':
        pdf = FPDF(orientation='L', unit='mm', format='A4') # Landscape
        pdf.set_auto_page_break(auto=False) # Matikan auto-break agar tabel multiline tidak rusak
        pdf.add_page()
        
        # Header Laporan
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=f"Laporan Manajemen Risiko KPPN - {quarter or 'Semua Triwulan'} {year}", ln=True, align='C')
        pdf.ln(3)
        
        # Konfigurasi Kolom
        cols = ["Kode IKU", "PIC", "Indikator Risiko Utama", "Kejadian Risiko", "P26", "R26", "Prev Q", "Curr Q", "Alasan/Mitigasi"]
        widths = [23, 16, 48, 48, 9, 9, 23, 23, 78] # Total lebar = 277mm (Maksimal kertas A4 Landscape)
        
        # Fungsi cetak header tabel
        def draw_table_header():
            pdf.set_font("Arial", 'B', 8)
            for i, col in enumerate(cols):
                pdf.cell(widths[i], 8, col, border=1, align='C')
            pdf.ln()
            
        draw_table_header()
        
        pdf.set_font("Arial", size=7)
        line_h = 4 # Tinggi per baris teks (enter)
        
        for row in data:
            pic_short = str(row['PIC']).replace("Seksi", "").replace("Subbagian", "Subbag").strip()
            curr_text = f"{row['Triwulan']} (Skor:{row['Skor Risiko (Current)']})"
            
            # Kumpulkan data dalam 1 baris
            row_data = [
                str(row['Kode IKU']),
                pic_short,
                str(row['IRU']),
                str(row['Kejadian Risiko']),
                str(row['P26']),
                str(row['R26']),
                str(row['Triwulan Sebelumnya']),
                curr_text,
                str(row['Alasan Perubahan Risiko'])
            ]
            
            # --- ALGORITMA PENENTU TINGGI BARIS (DYNAMIC ROW HEIGHT) ---
            max_lines = 1
            for i, text in enumerate(row_data):
                text_width = pdf.get_string_width(text)
                estimated_lines = int((text_width / (widths[i] - 3)) + 1)
                total_lines = estimated_lines + text.count('\n')
                
                if total_lines > max_lines:
                    max_lines = total_lines
                    
            row_height = max_lines * line_h
            
            # --- CEK HALAMAN BARU ---
            if pdf.get_y() + row_height > 190:
                pdf.add_page()
                draw_table_header()
                pdf.set_font("Arial", size=7)
                
            y_before = pdf.get_y()
            
            # --- CETAK SETIAP KOTAK DALAM BARIS ---
            for i, text in enumerate(row_data):
                x_before = pdf.get_x()
                pdf.rect(x_before, y_before, widths[i], row_height)
                align = 'C' if i in [0, 1, 4, 5, 6, 7] else 'L'
                pdf.multi_cell(w=widths[i], h=line_h, txt=text, border=0, align=align)
                pdf.set_xy(x_before + widths[i], y_before)
                
            pdf.set_xy(10, y_before + row_height)
            
        pdf_output = io.BytesIO(pdf.output(dest='S').encode('latin1'))
        pdf_output.seek(0)
        return send_file(pdf_output, mimetype='application/pdf', as_attachment=True, download_name=f'{filename_base}.pdf')
        
    else:
        return jsonify({'status': 'error', 'message': 'Format ekspor tidak didukung.'}), 400

# ==========================================
# 3. ENDPOINT EXPORT ZIP (DUAL STORAGE: SUPABASE & GDRIVE)
# ==========================================
@laporan_bp.route('/export-zip', methods=['GET'])
@jwt_required()
def export_zip():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    quarter = request.args.get('quarter', '')
    year = request.args.get('year', datetime.now().year)
    
    query = db.session.query(RiskAssessment).filter(RiskAssessment.status == 'verified')
    if user.role != 'admin':
        query = query.filter(RiskAssessment.section == user.section)
    if quarter:
        query = query.filter(RiskAssessment.quarter == quarter)
    if year:
        query = query.filter(RiskAssessment.year == int(year))
        
    assessments = query.all()
    if not assessments:
        return jsonify({"status": "error", "message": f"Tidak ada data asesmen terverifikasi untuk {quarter} {year}."}), 404

    assessment_ids = [a.id for a in assessments]
    documents = SupportingDocument.query.filter(SupportingDocument.assessment_id.in_(assessment_ids)).all()
    
    if not documents:
        return jsonify({"status": "error", "message": "Tidak ada dokumen bukti fisik yang diunggah pada periode ini."}), 404

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for doc in documents:
            try:
                # Format folder: Nama_Seksi/KodeIKU_NamaFile
                section_name = doc.assessment.section.replace(" ", "_")
                arc_name = f"{section_name}/{doc.assessment.indicator.indicator_code}_{doc.original_filename}"
                
                # --- JIKA FILE LAMA (SUPABASE) ---
                if "." in doc.stored_filename:
                    if supabase_client:
                        file_data = supabase_client.storage.from_('bukti_pendukung').download(doc.stored_filename)
                        zf.writestr(arc_name, file_data)
                
                # --- JIKA FILE BARU (GOOGLE DRIVE) ---
                else:
                    if drive_service:
                        request_drive = drive_service.files().get_media(fileId=doc.stored_filename)
                        file_stream = io.BytesIO()
                        downloader = MediaIoBaseDownload(file_stream, request_drive)
                        
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                        
                        # Sisipkan hasil download GDrive ke dalam ZIP
                        zf.writestr(arc_name, file_stream.getvalue())

            except Exception as e:
                print(f"Gagal menyisipkan {doc.stored_filename} ke ZIP: {e}")

    memory_file.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        memory_file, 
        mimetype='application/zip', 
        as_attachment=True, 
        download_name=f'Arsip_Bukti_{quarter}_{year}_{timestamp}.zip'
    )