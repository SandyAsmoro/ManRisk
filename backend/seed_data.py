from app import create_app, db
from models import RiskAssessment
import uuid

app = create_app()

with app.app_context():
    # Pastikan ID admin ini sesuai dengan ID admin yang ada di tabel users Anda
    admin_id = 'da71c1f3-aa8d-4c9a-9925-59e98d981e92' 

    demo = RiskAssessment(
        indicator_id=1,
        quarter='Q1',
        year=2024,
        section='Seksi MSKI',
        frequency=2,           # Sesuai models.py
        impact=3,              # Sesuai models.py
        risk_value=6,          # Sesuai models.py
        risk_category='Hijau', # Sesuai models.py
        status='submitted',
        submitted_by=admin_id
    )
    
    db.session.add(demo)
    db.session.commit()
    print("✅ Data dummy berhasil dimasukkan!")