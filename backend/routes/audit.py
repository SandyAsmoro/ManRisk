# ...\ManRiskMSKI\backend\routes\audit.py

import logging
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import AuditLog, User
from sqlalchemy import desc

audit_bp = Blueprint('audit', __name__)
logger = logging.getLogger(__name__)

# ==========================================
# FUNGSI HELPER GLOBAL UNTUK MENCATAT LOG
# ==========================================
def log_activity(user_id, action, resource_type, resource_id=None, details=None):
    """
    Panggil fungsi ini di rute manapun untuk mencatat jejak rekam aktivitas.
    """
    try:
        # Trik: Jika model tidak punya kolom 'details', kita gabungkan pesannya ke 'action'
        combined_action = f"{action} | {details}" if details else action
        
        log = AuditLog(
            user_id=user_id,
            action=combined_action, # <--- PERBAIKAN DI SINI
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None
            # Baris details=details dihapus agar tidak error
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Gagal mencatat audit log: {str(e)}")

# ==========================================
# ENDPOINT BACA LOG (KHUSUS ADMIN)
# ==========================================
@audit_bp.route('/', methods=['GET'])
@jwt_required()
def get_audit_logs():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user or user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'HTTP 403: Akses Ditolak. Khusus Admin.'}), 403
        
    # Ambil 500 log terbaru
    logs = db.session.query(AuditLog, User).outerjoin(User, AuditLog.user_id == User.id)\
        .order_by(desc(AuditLog.timestamp)).limit(500).all()
        
    data = []
    for log, u in logs:
        # Coba pisahkan kembali action dan details jika digabungkan dengan " | "
        parts = log.action.split(" | ", 1) if log.action else ["UNKNOWN"]
        clean_action = parts[0]
        extracted_details = parts[1] if len(parts) > 1 else "-"
        
        data.append({
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "username": u.username if u else "Sistem",
            "action": clean_action,
            "resource_type": log.resource_type,
            "details": extracted_details # Kirim ke frontend sebagai details
        })
        
    return jsonify({'status': 'success', 'data': data})