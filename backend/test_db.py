from app import create_app, db
from models import RiskAssessment

app = create_app()

with app.app_context():
    try:
        data = RiskAssessment.query.all()
        print(f"✅ Koneksi berhasil! Ditemukan {len(data)} data.")
    except Exception as e:
        print(f"❌ Error saat query: {e}")