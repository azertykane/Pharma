import os
from datetime import timedelta

class Config:
    # Clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Base de données - FORCER SQLite en local
    # Vérifier si on est en développement local
    IS_LOCAL_DEV = not os.environ.get('RENDER') and os.environ.get('FLASK_ENV') != 'production'
    
    if IS_LOCAL_DEV:
        # En développement local, utiliser SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///amicale.db'
        print("CONFIG: Utilisation de SQLite en développement local")
    else:
        # En production (Render), utiliser PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Convertir postgres:// en postgresql:// pour SQLAlchemy
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            SQLALCHEMY_DATABASE_URI = database_url
            print("CONFIG: Utilisation de PostgreSQL en production")
        else:
            # Fallback à SQLite si DATABASE_URL n'existe pas
            SQLALCHEMY_DATABASE_URI = 'sqlite:///amicale.db'
            print("CONFIG: DATABASE_URL non trouvé, utilisation de SQLite")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max
    
    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'rashidtoure730@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'rashidtoure730@gmail.com')
    
    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Production settings
    DEBUG = os.environ.get('FLASK_ENV') != 'production'
    
class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'  # Forcer HTTPS
    
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SUPPRESS_SEND = True  # Ne pas envoyer d'emails en développement