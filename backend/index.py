import os
import sys

# Memaksa Vercel untuk mengenali folder tempat index.py ini berada
# sehingga file seperti extensions.py dan models.py bisa dibaca.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import create_app

# Vercel akan membaca variabel ini
app = create_app()