# ...\ManRiskMSKI\backend\routes\admin.py

from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, DataError
from extensions import db
from models import User, RiskAssessment, RiskIndicator, SupportingDocument
from routes.audit import log_activity

admin_bp = Blueprint('admin', __name__)

# FUNGSI HELPER: Memeriksa apakah user adalah admin
def check_is_admin():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user or user.role != 'admin':
        return False, None
    return True, user

@admin_bp.route('/', methods=['GET'])
@jwt_required()
def index():
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403
    return jsonify({"status": "success", "message": "Admin API siap digunakan"})

@admin_bp.route('/assessments/pending', methods=['GET'])
@jwt_required()
def get_pending_assessments():
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403

    assessments = db.session.query(RiskAssessment, RiskIndicator)\
        .join(RiskIndicator)\
        .filter(RiskAssessment.status == 'submitted')\
        .order_by(RiskAssessment.submitted_at.desc())\
        .all()
    
    data = []
    for ass, ind in assessments:
        # Cek apakah ada dokumen pendukung untuk asesmen ini
        doc = SupportingDocument.query.filter_by(assessment_id=ass.id).first()
        
        data.append({
            "id": ass.id,
            "section": ass.section,
            "indicator_code": ind.indicator_code,
            "indicator_name": ind.indicator_name,
            "quarter": ass.quarter,
            "year": ass.year,
            "risk_category": ass.risk_category,
            "risk_value": ass.risk_value,
            "submitted_at": ass.submitted_at.isoformat() if ass.submitted_at else None,
            "has_document": True if doc else False,
            "document_name": doc.original_filename if doc else None
        })
    return jsonify({"status": "success", "data": data})

@admin_bp.route('/assessments/<assessment_id>/verify', methods=['POST'])
@jwt_required()
def verify_assessment(assessment_id):
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403
        
    data = request.json or {}
    action = data.get('action') 
    
    ass = db.session.get(RiskAssessment, assessment_id)
    if not ass:
        return jsonify({'status': 'error', 'message': 'Data asesmen risiko tidak ditemukan.'}), 404
        
    try:
        if action == 'approve':
            ass.status = 'verified'
            ass.verified_at = datetime.utcnow()
            message = "Laporan berhasil disetujui (Verified) secara resmi!"
            # Catat ke log
            log_activity(user.id, "APPROVE_DATA", "RiskAssessment", assessment_id, f"Data ID {assessment_id} dari {ass.section} disetujui oleh {user.username}")
            
        elif action == 'reject':
            ass.status = 'draft' # Dikembalikan ke draft agar user bisa edit lagi
            ass.submitted_at = None
            message = "Laporan ditolak (Reject) dan dikembalikan ke seksi untuk direvisi."
            # Catat ke log
            log_activity(user.id, "REJECT_DATA", "RiskAssessment", assessment_id, f"Data ID {assessment_id} dari {ass.section} ditolak oleh {user.username}")
            
        else:
            return jsonify({'status': 'error', 'message': 'Aksi tidak valid (gunakan approve/reject).'}), 400

        db.session.commit()
        return jsonify({'status': 'success', 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Gagal memproses verifikasi: {str(e)}'}), 500


# ===========================================================================
# 🚨 [ADMIN-CRUD] Manajemen Master Data Indikator & Nilai P26/R26
# ===========================================================================
#
# CATATAN PENTING:
# Kolom fisik di database bernama 'r26_target', BUKAN 'r26_initial'.
# Agar AdminIndicator.vue (yang sudah memakai key 'r26_initial') tidak perlu
# diubah, payload/response endpoint ini sengaja di-alias: terima & kembalikan
# 'r26_initial', lalu di backend dipetakan ke kolom 'r26_target'.
#
# Kolom 'indicator_code' di database dibatasi VARCHAR(20) — divalidasi ketat
# di sini supaya tidak gagal di level DB dengan error yang membingungkan.

def _serialize_indicator(ind):
    return {
        "id": ind.id,
        "indicator_code": ind.indicator_code,
        "indicator_name": ind.indicator_name,
        "indicator_description": ind.indicator_description,
        "indicator_type": ind.indicator_type,
        "pic_section": ind.pic_section,
        "secondary_pics": ind.secondary_pics,
        "is_active": ind.is_active,
        "iru_description": ind.iru_description,
        "p26_initial": ind.p26_initial,
        "r26_initial": ind.r26_target,  # alias, lihat catatan di atas
        "created_at": ind.created_at.isoformat() if ind.created_at else None,
        "updated_at": ind.updated_at.isoformat() if ind.updated_at else None,
    }


def _parse_score(value, field_label):
    """Konversi nilai skor (P26/R26) ke integer. Kembalikan (nilai, error)."""
    if value is None or value == '':
        return None, None
    try:
        return int(round(float(value))), None
    except (TypeError, ValueError):
        return None, f"{field_label} harus berupa angka."


@admin_bp.route('/indicators', methods=['GET'])
@jwt_required()
def get_all_indicators_admin():
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403

    indicators = RiskIndicator.query.order_by(RiskIndicator.indicator_code.asc()).all()
    return jsonify({"status": "success", "data": [_serialize_indicator(i) for i in indicators]})


@admin_bp.route('/indicators', methods=['POST'])
@jwt_required()
def create_indicator_admin():
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403

    data = request.json or {}

    indicator_code = (data.get('indicator_code') or '').strip()
    indicator_name = (data.get('indicator_name') or '').strip()

    errors = []
    if not indicator_code:
        errors.append('Kode indikator wajib diisi.')
    elif len(indicator_code) > 20:
        errors.append('Kode indikator maksimal 20 karakter (batasan kolom di database).')
    if not indicator_name:
        errors.append('Nama indikator wajib diisi.')

    p26_initial, err_p26 = _parse_score(data.get('p26_initial'), 'P26')
    if err_p26:
        errors.append(err_p26)
    r26_target, err_r26 = _parse_score(data.get('r26_initial'), 'R26')
    if err_r26:
        errors.append(err_r26)

    if errors:
        return jsonify({'status': 'error', 'message': ' '.join(errors)}), 400

    if RiskIndicator.query.filter_by(indicator_code=indicator_code).first():
        return jsonify({'status': 'error', 'message': f"Kode indikator '{indicator_code}' sudah digunakan. Gunakan kode lain."}), 400

    try:
        new_indicator = RiskIndicator(
            indicator_code=indicator_code,
            indicator_name=indicator_name,
            indicator_description=data.get('indicator_description') or None,
            indicator_type=(data.get('indicator_type') or '').strip() or None,
            pic_section=(data.get('pic_section') or '').strip() or None,
            secondary_pics=(data.get('secondary_pics') or '').strip() or None,
            iru_description=data.get('iru_description') or None,
            p26_initial=p26_initial,
            r26_target=r26_target,
            is_active=data.get('is_active', True),
        )
        db.session.add(new_indicator)
        db.session.commit()

        log_activity(user.id, "CREATE_INDICATOR", "RiskIndicator", new_indicator.id, f"Indikator '{indicator_code}' dibuat oleh {user.username}")
        return jsonify({'status': 'success', 'message': 'Indikator baru berhasil disimpan.', 'data': _serialize_indicator(new_indicator)}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f"Kode indikator '{indicator_code}' sudah digunakan. Gunakan kode lain."}), 400
    except DataError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Salah satu nilai melebihi batas panjang kolom di database.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Gagal menyimpan indikator: {str(e)}'}), 500


@admin_bp.route('/indicators/<int:indicator_id>', methods=['PUT'])
@jwt_required()
def update_indicator_admin(indicator_id):
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403

    indicator = db.session.get(RiskIndicator, indicator_id)
    if not indicator:
        return jsonify({'status': 'error', 'message': 'Indikator tidak ditemukan.'}), 404

    data = request.json or {}
    errors = []

    if 'indicator_code' in data:
        new_code = (data.get('indicator_code') or '').strip()
        if not new_code:
            errors.append('Kode indikator wajib diisi.')
        elif len(new_code) > 20:
            errors.append('Kode indikator maksimal 20 karakter (batasan kolom di database).')
        elif new_code != indicator.indicator_code and RiskIndicator.query.filter_by(indicator_code=new_code).first():
            errors.append(f"Kode indikator '{new_code}' sudah digunakan oleh indikator lain.")
    else:
        new_code = indicator.indicator_code

    if 'indicator_name' in data:
        new_name = (data.get('indicator_name') or '').strip()
        if not new_name:
            errors.append('Nama indikator wajib diisi.')
    else:
        new_name = indicator.indicator_name

    p26_initial, err_p26 = _parse_score(data.get('p26_initial', indicator.p26_initial), 'P26')
    if err_p26:
        errors.append(err_p26)
    r26_target, err_r26 = _parse_score(data.get('r26_initial', indicator.r26_target), 'R26')
    if err_r26:
        errors.append(err_r26)

    if errors:
        return jsonify({'status': 'error', 'message': ' '.join(errors)}), 400

    try:
        indicator.indicator_code = new_code
        indicator.indicator_name = new_name
        indicator.indicator_description = data.get('indicator_description', indicator.indicator_description)
        indicator.indicator_type = data.get('indicator_type', indicator.indicator_type)
        indicator.pic_section = data.get('pic_section', indicator.pic_section)
        indicator.secondary_pics = data.get('secondary_pics', indicator.secondary_pics)
        indicator.iru_description = data.get('iru_description', indicator.iru_description)
        indicator.p26_initial = p26_initial
        indicator.r26_target = r26_target
        indicator.is_active = data.get('is_active', indicator.is_active)
        indicator.updated_at = datetime.utcnow()

        db.session.commit()

        log_activity(user.id, "UPDATE_INDICATOR", "RiskIndicator", indicator.id, f"Indikator '{indicator.indicator_code}' diperbarui oleh {user.username}")
        return jsonify({'status': 'success', 'message': 'Data indikator berhasil diperbarui.', 'data': _serialize_indicator(indicator)})

    except IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f"Kode indikator '{new_code}' sudah digunakan oleh indikator lain."}), 400
    except DataError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Salah satu nilai melebihi batas panjang kolom di database.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Gagal memperbarui indikator: {str(e)}'}), 500


@admin_bp.route('/indicators/<int:indicator_id>', methods=['DELETE'])
@jwt_required()
def delete_indicator_admin(indicator_id):
    is_admin, user = check_is_admin()
    if not is_admin:
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Halaman khusus Administrator.'}), 403

    indicator = db.session.get(RiskIndicator, indicator_id)
    if not indicator:
        return jsonify({'status': 'error', 'message': 'Indikator tidak ditemukan.'}), 404

    indicator_code = indicator.indicator_code

    try:
        db.session.delete(indicator)
        db.session.commit()
        log_activity(user.id, "DELETE_INDICATOR", "RiskIndicator", indicator_id, f"Indikator '{indicator_code}' dihapus oleh {user.username}")
        return jsonify({'status': 'success', 'message': 'Indikator berhasil dihapus.'})

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f"Indikator '{indicator_code}' tidak dapat dihapus karena sudah memiliki data asesmen risiko terkait. Nonaktifkan saja indikator ini (toggle status) jika sudah tidak dipakai."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Gagal menghapus indikator: {str(e)}'}), 500