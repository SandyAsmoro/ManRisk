# ...\ManRiskMSKI\backend\app.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Manajemen Risiko KPPN
Main Flask Application — [UPDATED T14 - Health Check & T10 Password Guard]
"""

import os
import logging
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv
from extensions import db
from models import JWTBlacklist, User

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'manrisk-fallback-secret-key-kppn-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'manrisk-jwt-secret-very-secure-2026')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # PERBAIKAN CORS FINAL: Bersihkan string origin, lalu daftarkan ke flask-cors
    # Ambil nilai dari env. Jika kosong, gunakan default Netlify
    raw_origins = os.getenv('CORS_ORIGINS', 'https://manriskmski.netlify.app')
    allowed_origins = [origin.strip().rstrip('/') for origin in raw_origins.split(',')]
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = db.session.query(JWTBlacklist).filter_by(jti=jti).scalar()
        return token is not None

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"status": "error", "message": "Token otorisasi tidak ditemukan."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"status": "error", "message": "Token tidak valid atau sudah kedaluwarsa."}), 401

    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            return jsonify({
                "status": "healthy",
                "message": "Sistem API dan Database berjalan normal",
                "version": "1.0.0"
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "status": "unhealthy",
                "message": "Koneksi database terputus"
            }), 503

    @app.before_request
    def check_password_change_requirement():
        excluded_endpoints = ['/api/auth/login', '/api/auth/logout', '/api/auth/change-password']
        
        if request.path.startswith('/api/') and request.method != 'OPTIONS' and request.path not in excluded_endpoints:
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                
                if user_id:
                    user = db.session.get(User, user_id)
                    if user and getattr(user, 'must_change_password', False):
                        return jsonify({
                            "status": "error",
                            "message": "Wajib ganti password terlebih dahulu.",
                            "code": 403
                        }), 403
            except Exception:
                pass

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.risiko import risiko_bp
    from routes.matriks import matriks_bp
    from routes.laporan import laporan_bp
    from routes.admin import admin_bp
    from routes.audit import audit_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(risiko_bp, url_prefix='/api/risiko')
    app.register_blueprint(matriks_bp, url_prefix='/api/matriks')
    app.register_blueprint(laporan_bp, url_prefix='/api/laporan')
    app.register_blueprint(admin_bp, url_prefix='/api/admin') 
    app.register_blueprint(audit_bp, url_prefix='/api/audit') 

    logger.info("Aplikasi terhubung dan seluruh rute berhasil diamankan.")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)