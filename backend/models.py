# ...\ManRiskMSKI\backend\models.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistem Manajemen Risiko KPPN
SQLAlchemy Database Models
"""

import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    section = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    # [T10] Flag wajib ganti password
    must_change_password = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assessments = db.relationship('RiskAssessment', backref='submitter', lazy=True)

class RiskIndicator(db.Model):
    __tablename__ = 'risk_indicators'

    id = db.Column(db.Integer, primary_key=True)
    indicator_code = db.Column(db.String(50), unique=True, nullable=False) # Berisi Kode IKU & Kode Risiko
    indicator_name = db.Column(db.Text, nullable=False)
    indicator_description = db.Column(db.Text) # Berisi Kejadian Risiko
    indicator_type = db.Column(db.String(50), nullable=True) # 🚨 [ADMIN-CRUD] Kolom sudah ada di DB, baru dipetakan di sini
    iru_description = db.Column(db.Text) # 🚨 Kolom Baru: IRU
    pic_section = db.Column(db.String(100), nullable=False)
    
    # [T15] Kolom untuk PIC Pendamping (Read-only)
    secondary_pics = db.Column(db.String(100), nullable=True) 
    p26_initial = db.Column(db.Integer, nullable=True) # Nilai P26 Awal
    r26_target = db.Column(db.Integer, nullable=True) # Nilai R26 Target
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # 🚨 [ADMIN-CRUD] Kolom sudah ada di DB, baru dipetakan di sini

class RiskMatrixMapping(db.Model):
    __tablename__ = 'risk_matrix_mapping'

    id = db.Column(db.Integer, primary_key=True)
    risk_value = db.Column(db.Integer, unique=True, nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    color_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    mitigation_level = db.Column(db.String(50))

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    indicator_id = db.Column(db.Integer, db.ForeignKey('risk_indicators.id'), nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    risk_value = db.Column(db.Integer, nullable=False)
    risk_category = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(100), nullable=False)
    quarter = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    
    change_reason = db.Column(db.Text)
    mitigation_action = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    
    previous_quarter = db.Column(db.String(10))
    previous_risk_value = db.Column(db.Integer)
    risk_change = db.Column(db.Integer)
    
    submitted_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_by = db.Column(UUID(as_uuid=True), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('SupportingDocument', backref='assessment', cascade='all, delete-orphan', lazy=True)

class SupportingDocument(db.Model):
    __tablename__ = 'supporting_documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('risk_assessments.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(100))
    resource_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default='success')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# [T09] JWT Blacklist
class JWTBlacklist(db.Model):
    __tablename__ = 'jwt_blacklist'
    jti = db.Column(db.String(36), primary_key=True)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)