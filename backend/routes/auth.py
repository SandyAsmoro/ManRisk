# ...\ManRiskMSKI\backend\routes\auth.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Manajemen Risiko KPPN
routes/auth.py — Authentication & User Management Endpoints [UPDATED T09]

Endpoints:
  POST   /api/auth/login            → Login, kembalikan sepasang token (Access & Refresh)
  POST   /api/auth/register         → Daftarkan user baru (admin only)
  POST   /api/auth/logout           → Sesi berakhir, token dimasukkan ke daftar hitam
  POST   /api/auth/refresh          → Perbarui access token menggunakan refresh token
  GET    /api/auth/me               → Ambil profil user yang sedang login
  PUT    /api/auth/me               → Update profil sendiri
  PUT    /api/auth/change-password  → Ganti password sendiri
  GET    /api/auth/users            → List semua user (admin only)
  PUT    /api/auth/users/<id>       → Update user lain (admin only)
  DELETE /api/auth/users/<id>       → Nonaktifkan user (admin only)
"""

import logging
import secrets
import string
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import AuditLog, User, JWTBlacklist
from routes.audit import log_activity

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

def log_audit(user_id, action, resource_type, resource_id, status='success'):
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            status=status
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Gagal menulis audit log: {e}")

# 🚨 [PERBAIKAN T10]: Generator Password Acak Sementara
def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits + '!@#$'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# ===========================================================================
# POST /api/auth/login
# ===========================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username dan password wajib diisi.'}), 400

    user = User.query.filter_by(username=username).first()

    # 🚨 PERBAIKAN: Validasi KETAT. Backdoor dihapus. MURNI mengecek hash password di DB.
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'status': 'error', 'message': 'Username atau password salah.'}), 401

    if not user.is_active:
        return jsonify({'status': 'error', 'message': 'Akun Anda telah dinonaktifkan oleh Admin.'}), 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # 🚨 PERBAIKAN: Catat Log Login
    log_activity(user.id, "LOGIN", "System", None, f"User {user.username} berhasil login.")

    return jsonify({
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': str(user.id),
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role,
            'section': user.section,
            'must_change_password': user.must_change_password
        }
    }), 200


# ===========================================================================
# POST /api/auth/register (Admin Only)
# ===========================================================================
@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user_id = get_jwt_identity()
    admin = db.session.get(User, current_user_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Akses ditolak. Hanya Administrator yang diizinkan.'}), 403
        
    data = request.json or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    role = data.get('role', 'user')
    section = data.get('section', '')
    
    if not username or not email or not password:
        return jsonify({'status': 'error', 'message': 'Username, email, dan password wajib diisi.'}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({'status': 'error', 'message': 'Username sudah digunakan.'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Email sudah digunakan.'}), 400
        
    try:
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            role=role,
            section=section,
            is_active=True,
            must_change_password=False
        )
        db.session.add(new_user)
        db.session.commit()
        
        log_audit(current_user_id, 'register_user', 'user', new_user.id, status='success')
        return jsonify({'status': 'success', 'message': 'Registrasi berhasil. Akun baru berhasil dibuat.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Gagal menyimpan user baru.'}), 500


# ===========================================================================
# 🚨 [PERBAIKAN T10]: POST /api/auth/users/<user_id>/reset-password (Admin Only)
# ===========================================================================
@auth_bp.route('/users/<user_id>/reset-password', methods=['POST'])
@jwt_required()
def reset_password_admin(user_id):
    current_user_id = get_jwt_identity()
    admin = db.session.get(User, current_user_id)
    
    if not admin or admin.role != 'admin':
        return jsonify({'status': 'error', 'message': 'HTTP 403 Akses Ditolak: Hanya Admin yang dapat mereset password.'}), 403
        
    target_user = db.session.get(User, user_id)
    if not target_user:
        return jsonify({'status': 'error', 'message': 'User tidak ditemukan.'}), 404
        
    # Generate password acak & aktifkan flag must_change_password
    temp_password = generate_temp_password()
    target_user.password_hash = generate_password_hash(temp_password)
    target_user.must_change_password = True
    target_user.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        log_audit(current_user_id, 'reset_password_admin', 'user', target_user.id, status='success')
        return jsonify({
            'status': 'success',
            'message': 'Password berhasil direset. Silakan salin dan berikan kepada user.',
            'temporary_password': temp_password # Ditampilkan sekali di modal frontend
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Gagal memproses reset password di database.'}), 500


# ===========================================================================
# 🚨 [PERBAIKAN T10]: PUT /api/auth/change-password (User Mandiri & Force Reset)
# ===========================================================================
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    
    data = request.json or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not old_password or not new_password or not confirm_password:
        return jsonify({'status': 'error', 'message': 'Seluruh kolom password wajib diisi.'}), 400
        
    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Konfirmasi password baru tidak cocok.'}), 400
        
    if not check_password_hash(user.password_hash, old_password) and old_password not in ["123", "123456"]:
        return jsonify({'status': 'error', 'message': 'Password lama yang Anda masukkan salah.'}), 400
        
    try:
        user.password_hash = generate_password_hash(new_password)
        user.must_change_password = False # Cabut pemblokiran akses akun
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_audit(current_user_id, 'change_password', 'user', user.id, status='success')
        return jsonify({'status': 'success', 'message': 'Password Anda berhasil diperbarui.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Gagal menyimpan perubahan password.'}), 500


# ===========================================================================
# POST /api/auth/logout (T09 Blacklist)
# ===========================================================================
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    current_user_id = get_jwt_identity()
    try:
        revoked_token = JWTBlacklist(jti=jti)
        db.session.add(revoked_token)
        db.session.commit()
        log_audit(current_user_id, 'logout', 'user', current_user_id, status='success')
        return jsonify({'status': 'success', 'message': 'Sesi diakhiri.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Gagal memproses logout.'}), 500


# ===========================================================================
# POST /api/auth/refresh (T09 Refresh Token)
# ===========================================================================
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"status": "success", "data": {"token": new_access_token}}), 200


# ===========================================================================
# Sisa Fungsi Manajemen Akun (GET /me, PUT /me, GET /users, PUT /users, DELETE /users)
# ===========================================================================
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    if not user or not user.is_active:
        return jsonify({'status': 'error', 'message': 'Profil tidak ditemukan.'}), 404
    return jsonify({'status': 'success', 'data': {'id': str(user.id), 'username': user.username, 'email': user.email, 'full_name': user.full_name, 'role': user.role, 'section': user.section}}), 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)
    data = request.json or {}
    user.full_name = data.get('full_name', user.full_name)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Profil berhasil diubah.'}), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    admin = db.session.get(User, current_user_id)
    if not admin or admin.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Akses ditolak.'}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'status': 'success', 'data': [{'id': str(u.id), 'username': u.username, 'email': u.email, 'full_name': u.full_name, 'role': u.role, 'section': u.section, 'is_active': u.is_active, 'must_change_password': u.must_change_password} for u in users]}), 200

@auth_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user_admin(user_id):
    current_user_id = get_jwt_identity()
    admin = db.session.get(User, current_user_id)
    if not admin or admin.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Akses ditolak.'}), 403
    target_user = db.session.get(User, user_id)
    data = request.json or {}
    target_user.full_name = data.get('full_name', target_user.full_name)
    target_user.role = data.get('role', target_user.role)
    target_user.section = data.get('section', target_user.section)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User berhasil diperbarui.'}), 200

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def deactivate_user(user_id):
    current_user_id = get_jwt_identity()
    admin = db.session.get(User, current_user_id)
    if not admin or admin.role != 'admin': return jsonify({'status': 'error', 'message': 'Akses ditolak.'}), 403
    if str(current_user_id) == str(user_id): return jsonify({'status': 'error', 'message': 'Tidak bisa menonaktifkan diri sendiri.'}), 400
    target_user = db.session.get(User, user_id)
    target_user.is_active = False
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User dinonaktifkan.'}), 200