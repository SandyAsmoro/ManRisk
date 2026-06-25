# ...\ManRiskMSKI\backend\routes\dashboard.py

import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import RiskAssessment, User, RiskMatrixMapping

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "Dashboard API siap digunakan"})

@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404
        
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
    
    # 🚨 PERBAIKAN: kategori sebelumnya hardcode ('Biru','Hijau','Kuning','Jingga','Merah')
    # padahal nama kategori asli di tabel risk_matrix_mapping sudah jadi 'Hijau Tua' &
    # 'Oranye'. Hitungan tetap akurat berkat fallback else di bawah, tapi key 'Hijau' &
    # 'Jingga' jadi key hantu yang tak pernah terisi & tidak konsisten dengan
    # get_matriks_summary() di routes/matriks.py. Sekarang kategori diambil langsung
    # dari DB supaya kedua endpoint summary selalu sinkron & ikut menyesuaikan kalau
    # kategori di database diubah lagi di kemudian hari.
    distinct_categories = db.session.query(RiskMatrixMapping.category).distinct().all()
    summary = {cat[0]: 0 for cat in distinct_categories}

    for a in assessments:
        cat = a.risk_category
        summary[cat] = summary.get(cat, 0) + 1
            
    return jsonify({
        "status": "success",
        "data": summary
    }), 200