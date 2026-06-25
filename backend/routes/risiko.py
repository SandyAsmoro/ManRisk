# ...\ManRiskMSKI\backend\routes\risiko.py

import os
import logging
import uuid
import io
from supabase import create_client, Client
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import RiskIndicator, RiskAssessment, RiskMatrixMapping, User, SupportingDocument
from datetime import datetime
from utils.decorators import check_section_access
from config import is_editable
from werkzeug.utils import secure_filename
from sqlalchemy import asc, case

logger = logging.getLogger(__name__)
risiko_bp = Blueprint('risiko', __name__)

# 🚨 INISIALISASI SUPABASE CLIENT
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase_client: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
# UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'bukti_pendukung')


def get_previous_quarter(current_quarter, current_year):
    if current_quarter == 'Q1':
        return 'Q4', current_year - 1
    else:
        q_num = int(current_quarter[1])
        return f'Q{q_num - 1}', current_year

# ==========================================
# 🚨 FUNGSI BARU: VALIDASI QUARTER-BASED LOCKING
# ==========================================

def check_quarter_lock(quarter, user_role):
    """
    Mengembalikan (is_allowed, error_message).
    Admin diizinkan mengedit/input kapan saja.
    """
    if user_role == 'admin':
        return True, ""

    current_month = datetime.utcnow().month

    quarter_months = {
        'Q1': [1, 2, 3],
        'Q2': [4, 5, 6],
        'Q3': [7, 8, 9],
        'Q4': [10, 11, 12]
    }

    if quarter not in quarter_months:
        return False, "Format triwulan tidak valid."

    if current_month not in quarter_months[quarter]:
        return False, f"Periode input/edit untuk Triwulan {quarter} telah ditutup atau belum dimulai."

    return True, ""

# ==========================================
# ENDPOINT GET INDIKATOR
# ==========================================

@risiko_bp.route('/indicators', methods=['GET'])
@jwt_required()
def get_indicators():
    # indicators = RiskIndicator.query.filter_by(is_active=True).all()
    # SESUDAH DIUBAH:
    # 1. Atur bobot prioritas baru (Bobot terkecil akan muncul paling atas)
    sort_priority = case(
        (RiskIndicator.indicator_code.startswith('NON-IKU'), 2),     # Prioritas 2 (Tengah)
        (RiskIndicator.indicator_code.startswith('MANDATORY'), 3),   # Prioritas 3 (Bawah)
        else_=1                                                     # Prioritas 1 (Teratas: Indikator lainnya)
    )

    # 2. Tarik data dari database dengan filter aktif dan urutan ganda
    indicators = RiskIndicator.query.filter_by(is_active=True).order_by(
        sort_priority,                      # 1. Urutkan berdasarkan urutan kelompok prioritas baru
        RiskIndicator.indicator_code.asc()  # 2. Urutkan A-Z secara alfabetis di dalam masing-masing kelompok
    ).all()
    return jsonify({
        "status": "success",
        "data": [{
            "id": i.id,
            "code": i.indicator_code,  # Otomatis berisi Gabungan IKU - Risiko
            "name": i.indicator_name,
            "kejadian_risiko": i.indicator_description,  # Membaca dari kolom lama
            "iru": i.iru_description,  # Membaca kolom baru
            "p26": i.p26_initial,
            "r26": i.r26_target,
            "pic": i.pic_section,
            "secondary_pics": i.secondary_pics
        } for i in indicators]
    })

# ==========================================
# ENDPOINT GET RIWAYAT ASESMEN
# ==========================================

@risiko_bp.route('/assessments', methods=['GET'])
@jwt_required()
def get_assessments():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    quarter = request.args.get('quarter')
    year = request.args.get('year')

    query = RiskAssessment.query

    if user.role != 'admin':
        query = query.filter_by(section=user.section)

    if quarter:
        query = query.filter_by(quarter=quarter)
    if year:
        try:
            query = query.filter_by(year=int(year))
        except ValueError:
            pass

    assessments = query.all()

    data = []
    for ass in assessments:
        indicator = db.session.get(RiskIndicator, ass.indicator_id)
        if not indicator:
            continue

        doc = SupportingDocument.query.filter_by(assessment_id=ass.id).first()

        data.append({
            "id": ass.id,
            "indicator_id": indicator.id,
            "indicator_code": indicator.indicator_code,
            "indicator_name": indicator.indicator_name,
            "quarter": ass.quarter,
            "year": ass.year,
            "frequency": ass.frequency,
            "impact": ass.impact,
            "risk_value": ass.risk_value,
            "risk_category": ass.risk_category,
            "mitigation_action": ass.mitigation_action,
            "status": ass.status,
            "created_at": ass.created_at.isoformat() if ass.created_at else None,
            "has_document": True if doc else False,
            "document_name": doc.original_filename if doc else None
        })

    return jsonify({"status": "success", "data": data})

# ==========================================
# ENDPOINT CREATE (INPUT DATA BARU)
# ==========================================

@risiko_bp.route('/assessment', methods=['POST'])
@jwt_required()
def create_assessment():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    data = request.json
    quarter = data.get('quarter')
    year = int(data.get('year', datetime.utcnow().year))
    indicator_id = data.get('indicator_id')

    # 1. Validasi Lock Quarter (Apakah masih dalam batas waktu?)
    is_unlocked, msg = check_quarter_lock(quarter, user.role)
    if not is_unlocked and user.role != 'admin':
        return jsonify({'status': 'error', 'message': msg}), 403

    # 2. Cegah Duplikasi Input
    existing = RiskAssessment.query.filter_by(
        indicator_id=indicator_id,
        section=user.section,
        quarter=quarter,
        year=year
    ).first()

    if existing:
        return jsonify({'status': 'error', 'message': 'Data untuk indikator ini sudah diisi pada kuartal tersebut. Silakan edit melalui menu "Riwayat & Edit Data".'}), 400

    # 3. Hitung Matriks Risiko
    new_frequency = int(data.get('frequency', 1))
    new_impact = int(data.get('impact', 1))

    mapping_row = RiskMatrixMapping.query.filter_by(
        frequency=new_frequency, impact=new_impact).first()
    if not mapping_row:
        return jsonify({'status': 'error', 'message': 'Kombinasi nilai Frekuensi dan Dampak tidak valid.'}), 400

    # 4. Simpan ke Database
    assessment = RiskAssessment(
        indicator_id=indicator_id,
        section=user.section,
        quarter=quarter,
        year=year,
        frequency=new_frequency,
        impact=new_impact,
        risk_value=mapping_row.risk_value,
        risk_category=mapping_row.category,
        mitigation_action=data.get('mitigation_action', ''),
        status='draft'  # Status awal selalu draft sebelum di-Batch Submit
    )

    db.session.add(assessment)
    db.session.commit()

    return jsonify({"status": "success", "message": "Data asesmen risiko berhasil disimpan!"}), 201

# ==========================================
# ENDPOINT BATCH SUBMIT (KIRIM FINAL)
# ==========================================


@risiko_bp.route('/assessments/batch-submit', methods=['POST'])
@jwt_required()
def batch_submit():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    data = request.json
    quarter = data.get('quarter')
    year = int(data.get('year', datetime.utcnow().year))

    # 1. Validasi Lock Quarter
    is_unlocked, msg = check_quarter_lock(quarter, user.role)
    if not is_unlocked and user.role != 'admin':
        return jsonify({'status': 'error', 'message': msg}), 403

    # 2. Cari semua data draft milik seksi ini di kuartal ini
    drafts = RiskAssessment.query.filter_by(
        section=user.section,
        quarter=quarter,
        year=year,
        status='draft'
    ).all()

    if not drafts:
        return jsonify({'status': 'error', 'message': 'Tidak ada data (draft) baru yang bisa dikirim untuk periode ini.'}), 400

    # 3. Ubah status menjadi submitted
    for draft in drafts:
        draft.status = 'submitted'
        draft.submitted_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"status": "success", "message": f"Berhasil mengirim final {len(drafts)} indikator risiko untuk {quarter} Tahun {year}!"})

# ==========================================
# ENDPOINT HAPUS DOKUMEN BUKTI PENDUKUNG
# ==========================================
@risiko_bp.route('/assessments/<assessment_id>/document', methods=['DELETE'])
@jwt_required()
def delete_document(assessment_id):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    # 1. Validasi Akses
    has_access, assessment_or_error, status_code = check_section_access(assessment_id, user_id)
    if not has_access:
        return jsonify(assessment_or_error), status_code
        
    assessment = assessment_or_error
    
    # 2. Validasi Kunci Periode & Status
    is_unlocked, msg = check_quarter_lock(assessment.quarter, user.role)
    if not is_unlocked and user.role != 'admin':
        return jsonify({'status': 'error', 'message': msg}), 403
        
    if assessment.status == 'verified' and user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Data ini telah diverifikasi oleh Admin. Dokumen tidak dapat dihapus.'}), 403

    # 3. Cari Data Dokumen
    doc = SupportingDocument.query.filter_by(assessment_id=assessment_id).first()
    if not doc:
        return jsonify({'status': 'error', 'message': 'Dokumen bukti pendukung tidak ditemukan.'}), 404
        
    # 4. Hapus File Fisik di Supabase Storage
    if supabase_client:
        try:
            supabase_client.storage.from_('bukti_pendukung').remove([doc.stored_filename])
        except Exception as e:
            logger.error(f"Gagal menghapus file dari Supabase Storage: {str(e)}")
            # Tetap lanjut menghapus dari database meskipun file fisik di cloud gagal dihapus (misal file sudah hilang duluan)

    # 5. Hapus Catatan Metadata di Database
    try:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Dokumen bukti pendukung berhasil dihapus.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan internal: {str(e)}'}), 500
    
# ==========================================
# ENDPOINT UPDATE (EDIT DATA YANG SUDAH ADA)
# ==========================================
import uuid
from werkzeug.utils import secure_filename

@risiko_bp.route('/assessments/<assessment_id>', methods=['PUT'])
@jwt_required()
def update_assessment(assessment_id):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    has_access, assessment_or_error, status_code = check_section_access(assessment_id, user_id)
    if not has_access:
        return jsonify(assessment_or_error), status_code
        
    assessment = assessment_or_error

    try:
        is_unlocked, msg = check_quarter_lock(assessment.quarter, user.role)
        if not is_unlocked and user.role != 'admin':
            return jsonify({'status': 'error', 'message': msg}), 403
            
        if assessment.status == 'verified' and user.role != 'admin':
            return jsonify({'status': 'error', 'message': 'Data ini telah diverifikasi dan dikunci resmi oleh Admin. Tidak dapat diedit.'}), 403

        # 🚨 PERBAIKAN: Deteksi apakah request mengirim File (Form-Data) atau hanya Teks (JSON)
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form
            file = request.files.get('file')
        else:
            data = request.json or {}
            file = None

        new_frequency = int(data.get('frequency', assessment.frequency))
        new_impact = int(data.get('impact', assessment.impact))
        new_mitigation = data.get('mitigation_action', assessment.mitigation_action)

        mapping_row = RiskMatrixMapping.query.filter_by(frequency=new_frequency, impact=new_impact).first()
        if not mapping_row:
            return jsonify({'status': 'error', 'message': 'Kombinasi nilai Frekuensi dan Dampak tidak valid.'}), 400

        # Update nilai teks
        assessment.frequency = new_frequency
        assessment.impact = new_impact
        assessment.risk_value = mapping_row.risk_value
        assessment.risk_category = mapping_row.category
        assessment.mitigation_action = new_mitigation
        
        if assessment.status == 'reject':
            assessment.status = 'draft'
            
        # 🚨 PERBAIKAN: Proses upload file ke Supabase Storage
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            stored_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # Baca wujud fisik file menjadi urutan bytes
            file_bytes = file.read()
            
            if not supabase_client:
                return jsonify({'status': 'error', 'message': 'Konfigurasi Supabase Storage belum diatur di server.'}), 500

            # Kirim file ke cloud Supabase
            try:
                supabase_client.storage.from_('bukti_pendukung').upload(
                    path=stored_filename,
                    file=file_bytes,
                    file_options={"content-type": file.content_type}
                )
            except Exception as upload_error:
                # Gunakan update jika nama file kebetulan sama (jarang terjadi karena ada UUID)
                supabase_client.storage.from_('bukti_pendukung').update(
                    path=stored_filename,
                    file=file_bytes,
                    file_options={"content-type": file.content_type}
                )
            
            # Catat metadata ke Database PostgreSQL
            doc = SupportingDocument.query.filter_by(assessment_id=assessment.id).first()
            if doc:
                # Opsional: Hapus file lama di Supabase Storage untuk menghemat kuota
                try:
                    supabase_client.storage.from_('bukti_pendukung').remove([doc.stored_filename])
                except:
                    pass
                    
                doc.original_filename = filename
                doc.stored_filename = stored_filename
                doc.mime_type = file.content_type
            else:
                doc = SupportingDocument(
                    assessment_id=assessment.id,
                    original_filename=filename,
                    stored_filename=stored_filename,
                    mime_type=file.content_type
                )
                db.session.add(doc)

        db.session.commit()
        return jsonify({"status": "success", "message": "Data revisi profil risiko dan dokumen berhasil diperbarui!"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error update assessment: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan internal: {str(e)}'}), 500

# ==========================================
# ENDPOINT DELETE (HAPUS KESELURUHAN DATA ASESMEN)
# ==========================================
@risiko_bp.route('/assessments/<assessment_id>', methods=['DELETE'])
@jwt_required()
def delete_assessment(assessment_id):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    # 1. Cek Hak Akses (Pastikan hanya pemilik atau admin yang bisa menghapus)
    has_access, assessment_or_error, status_code = check_section_access(assessment_id, user_id)
    if not has_access:
        return jsonify(assessment_or_error), status_code

    assessment = assessment_or_error

    # 2. Validasi Kunci Periode & Status Verifikasi
    is_unlocked, msg = check_quarter_lock(assessment.quarter, user.role)
    if not is_unlocked and user.role != 'admin':
        return jsonify({'status': 'error', 'message': msg}), 403

    if assessment.status == 'verified' and user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Data ini telah disetujui (Verified) dan tidak dapat dihapus.'}), 403

    try:
        # 3. Cari dan Hapus Dokumen Fisik di Supabase (Jika Ada)
        doc = SupportingDocument.query.filter_by(assessment_id=assessment_id).first()
        if doc and supabase_client:
            try:
                supabase_client.storage.from_('bukti_pendukung').remove([doc.stored_filename])
            except Exception as e:
                logger.error(f"Gagal menghapus file dari Supabase Storage: {str(e)}")

        # 4. Hapus Asesmen dari Database
        # (Catatan: Baris tabel SupportingDocument akan ikut terhapus otomatis karena cascade='all, delete-orphan' di models.py)
        db.session.delete(assessment)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Data asesmen berhasil dihapus.'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error hapus asesmen: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Terjadi kesalahan internal saat menghapus data.'}), 500

# ==========================================
# ENDPOINT DOWNLOAD DOKUMEN BUKTI PENDUKUNG
# ==========================================

@risiko_bp.route('/assessments/<assessment_id>/document', methods=['GET'])
@jwt_required()
def download_document(assessment_id):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    has_access, assessment_or_error, status_code = check_section_access(assessment_id, user_id)
    if not has_access:
        return jsonify(assessment_or_error), status_code
        
    doc = SupportingDocument.query.filter_by(assessment_id=assessment_id).first()
    if not doc:
        return jsonify({'status': 'error', 'message': 'Dokumen bukti pendukung tidak ditemukan di database.'}), 404
        
    if not supabase_client:
        return jsonify({'status': 'error', 'message': 'Konfigurasi Cloud Storage gagal.'}), 500

    try:
        # Tarik data fisik file dari Supabase Storage dalam format bytes
        file_data = supabase_client.storage.from_('bukti_pendukung').download(doc.stored_filename)
        
        from flask import send_file
        import io
        return send_file(
            io.BytesIO(file_data), 
            mimetype=doc.mime_type, 
            as_attachment=True, 
            download_name=doc.original_filename
        )
    except Exception as e:
        logger.error(f"Gagal download file dari Supabase: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Gagal mengambil file dari Cloud Storage. File mungkin telah terhapus.'}), 500