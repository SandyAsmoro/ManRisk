# ...\ManRiskMSKI\backend\routes\matriks.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from sqlalchemy import func
from models import RiskAssessment, User, RiskIndicator

matriks_bp = Blueprint('matriks', __name__)

@matriks_bp.route('/summary/<quarter>', methods=['GET'])
@jwt_required()
def get_matriks_summary(quarter):
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    year = request.args.get('year', 2024)
    
    # Hitung jumlah asesmen berdasarkan kategori warna
    query = db.session.query(
        RiskAssessment.risk_category, 
        func.count(RiskAssessment.id)
    ).join(RiskIndicator).filter(RiskAssessment.quarter == quarter, RiskAssessment.year == year)
    
    # Filter Hak Akses
    if user.role != 'admin':
        query = query.filter(
            (RiskAssessment.section == user.section) | 
            (RiskIndicator.secondary_pics == user.section)
        )
        
    results = query.group_by(RiskAssessment.risk_category).all()
    
    # Mapping standar Kemenkeu (Nilai awal 0)
    summary = { "Biru": 0, "Hijau": 0, "Kuning": 0, "Jingga": 0, "Merah": 0 }
    
    # Memasukkan hasil query ke mapping yang sesuai
    for kategori, count in results:
        # Pengecekan aman jaga-jaga kalau ada nama kategori anomali (misal "Risiko Tinggi" bukan warnanya)
        if "Biru" in str(kategori) or "Rendah" in str(kategori) and "Sedang" not in str(kategori): summary["Biru"] += count
        elif "Hijau" in str(kategori) or "Sedang Rendah" in str(kategori): summary["Hijau"] += count
        elif "Kuning" in str(kategori) or "Sedang" in str(kategori): summary["Kuning"] += count
        elif "Jingga" in str(kategori) or "Tinggi" in str(kategori) and "Sangat" not in str(kategori): summary["Jingga"] += count
        elif "Merah" in str(kategori) or "Sangat Tinggi" in str(kategori): summary["Merah"] += count
        # Default map (fallback)
        elif kategori in summary: summary[kategori] = count

    return jsonify({"status": "success", "data": summary})