# ...\ManRiskMSKI\backend\routes\dashboard.py

import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import RiskAssessment, User

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
    
    # KUNCI HARUS SESUAI DENGAN ISI DATABASE (TABEL RiskMatrixMapping)
    summary = {
        'Biru': 0,
        'Hijau': 0,
        'Kuning': 0,
        'Jingga': 0,
        'Merah': 0
    }
    
    for a in assessments:
        cat = a.risk_category
        if cat in summary:
            summary[cat] += 1
        else:
            summary[cat] = summary.get(cat, 0) + 1
            
    return jsonify({
        "status": "success",
        "data": summary
    }), 200