# ...\ManRiskMSKI\backend\utils\decorators.py

from extensions import db
from models import User, RiskAssessment

def check_section_access(assessment_id, user_id):
    """
    Helper untuk memeriksa hak akses RBAC per seksi.
    Mengembalikan tuple: (has_access: bool, data_or_error_msg, status_code: int)
    """
    user = db.session.get(User, user_id)
    if not user:
        return False, {'status': 'error', 'message': 'Pengguna tidak valid.'}, 401

    assessment = db.session.get(RiskAssessment, assessment_id)
    if not assessment:
        return False, {'status': 'error', 'message': 'Data asesmen risiko tidak ditemukan.'}, 404

    # Pengecualian: Admin bisa mengakses dan mengedit data dari semua seksi
    if user.role == 'admin':
        return True, assessment, 200

    # Isolasi Seksi: Tolak jika seksi user berbeda dengan seksi data
    if str(assessment.section) != str(user.section):
        return False, {'status': 'error', 'message': 'HTTP 403 Akses Ditolak: Anda tidak diizinkan melihat atau mengubah data dari seksi lain.'}, 403

    return True, assessment, 200