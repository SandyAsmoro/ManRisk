from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

# Inisialisasi aplikasi Flask
app = create_app()

with app.app_context():
    # Cari user admin
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        # Timpa hash bcrypt lama dengan hash buatan Werkzeug
        # Menggunakan password default dari SETUP_GUIDE.md
        admin.password_hash = generate_password_hash('AdminSecure2024!')
        db.session.commit()
        print("✅ Password admin berhasil diubah ke format Werkzeug!")
    else:
        print("❌ User admin tidak ditemukan di database.")