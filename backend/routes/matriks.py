# ...\ManRiskMSKI\backend\routes\matriks.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from sqlalchemy import func
from models import RiskAssessment, User, RiskIndicator, RiskMatrixMapping # Pastikan Model ini ada

matriks_bp = Blueprint('matriks', __name__)

# ENDPOINT BARU: Digunakan oleh MatrixVisual.vue untuk menggambar Matriks
@matriks_bp.route('/mapping', methods=['GET'])
@jwt_required()
def get_matrix_mapping():
    mappings = db.session.query(RiskMatrixMapping).all()
    
    data = []
    for m in mappings:
        data.append({
            "id": m.id,
            "risk_value": m.risk_value,
            "frequency": m.frequency,
            "impact": m.impact,
            "category": m.category,
            "color_code": m.color_code,
            "description": m.description,
            "mitigation_level": m.mitigation_level
        })
        
    return jsonify({"status": "success", "data": data})

# ENDPOINT LAMA YANG DIPERBARUI: Dibuat dinamis membaca tabel RiskMatrixMapping
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
    
    # Dapatkan semua kategori unik langsung dari database (Tabel Mapping)
    distinct_categories = db.session.query(RiskMatrixMapping.category).distinct().all()
    summary = { cat[0]: 0 for cat in distinct_categories }
    
    # Memasukkan hasil query ke mapping yang sesuai secara eksak
    # (Hanya asumsikan nilai RiskAssessment.risk_category sinkron dengan nama kolom di RiskMatrixMapping)
    for kategori, count in results:
        if kategori in summary:
            summary[kategori] = count
        else:
            # Jika ada sisa data historis lama (fallback)
            summary[kategori] = count

    return jsonify({"status": "success", "data": summary})