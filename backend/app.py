# ...\ManRiskMSKI\backend\app.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Manajemen Risiko KPPN
Main Flask Application — Optimized for Vercel Serverless Deployment
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_migrate import Migrate
from dotenv import load_dotenv
from extensions import db
from models import User

load_dotenv()

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Konfigurasi Dasar
    app.config['JSON_AS_ASCII'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # Inisialisasi Ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # --- KONFIGURASI CORS PRODUKSI ---
    # Mengambil domain dari env atau default untuk keamanan
    allowed_origins = os.getenv('CORS_ORIGINS', 'https://ubiquitous-melomakarona-51e5fa.netlify.app').split(',')
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Penanganan Preflight Request (Sangat penting untuk Vercel)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return '', 200

    # Middleware pengecekan wajib ganti password
    @app.after_request
    def check_password_status(response):
        try:
            if request.endpoint and 'login' not in request.endpoint:
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
        return response

    # Blueprint Registration
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

    logger.info("Aplikasi terhubung dan seluruh rute terdaftar.")
    return app

# PENTING: Variabel 'app' harus didefinisikan secara global untuk Vercel
app = create_app()

if __name__ == '__main__':
    # Blok ini hanya berjalan di lokal
    app.run(debug=True, port=5000)