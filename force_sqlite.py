import os
import sys

# Forcer SQLite en supprimant les variables d'environnement problématiques
os.environ.pop('DATABASE_URL', None)
os.environ.pop('POSTGRES_URL', None)
os.environ.pop('PGDATABASE', None)
os.environ.pop('PGHOST', None)
os.environ.pop('PGPORT', None)
os.environ.pop('PGUSER', None)
os.environ.pop('PGPASSWORD', None)

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'application
from app import app

if __name__ == '__main__':
    print("Mode SQLite forcé pour le développement local")
    app.run(debug=True, port=5000)