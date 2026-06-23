from app import create_app
from extensions import db
from models import SupportingDocument

app = create_app()
with app.app_context():
    docs = SupportingDocument.query.all()
    print(f"\n[HASIL INVESTIGASI]")
    print(f"Database URL yang dipakai: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Jumlah dokumen ditemukan: {len(docs)}")
    
    for doc in docs:
        print(f"- ID: {doc.id} | Nama Asli: {doc.original_filename} | Tersimpan: {doc.stored_filename}")
    print("\n")