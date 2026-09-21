import os
import secrets
from pathlib import Path
from pymongo import MongoClient
from flask_sqlalchemy import SQLAlchemy
import redis

# Racine du projet : tous les chemins en dépendent, rien n'est codé en dur
BASE_DIR = Path(__file__).resolve().parent.parent

# Instance SQLAlchemy pour les users
db = SQLAlchemy()

# Instance Redis pour les sessions
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)  # set SECRET_KEY in production
    
    # MongoDB Configuration (pour logs et alerts)
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB = 'sentinelai_db'
    
    # Collections MongoDB
    LOGS_COLLECTION = 'logs'
    ALERTS_COLLECTION = 'alerts'
    
    # PostgreSQL Configuration (pour users)
    # Option 1: PostgreSQL (recommandé en production)
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/sentinelai_users'
    
    # Option 2: SQLite (simple, pour développement)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{(BASE_DIR / 'sentinelai_users.db').as_posix()}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration (pour sessions)
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis_client
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'sentinelai:session:'
    
    # Session TTL (en secondes)
    SESSION_TTL = 3600  # 1 heure
    
    # ML Model Path
    MODEL_PATH = str(BASE_DIR / 'ml' / 'model.pkl')
    DATASET_PATH = os.environ.get('SENTINELAI_DATASET', str(BASE_DIR / 'data' / 'final_dataset.csv'))
    
    # Flask
    # Sécurisé par défaut : pas de débogueur Werkzeug, écoute sur la machine locale uniquement.
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))

# MongoDB Connection (pour logs et alerts uniquement)
def get_mongo_db():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]
    return db

def init_mongo_indexes():
    """Initialise les index MongoDB pour logs et alerts uniquement"""
    db = get_mongo_db()
    
    # Index pour logs
    db.logs.create_index([('timestamp', -1)])
    db.logs.create_index([('source_ip', 1)])
    db.logs.create_index([('Label', 1)])
    db.logs.create_index([('event_type', 1)])
    
    # Index pour alerts
    db.alerts.create_index([('timestamp', -1)])
    db.alerts.create_index([('log_id', 1)])
    db.alerts.create_index([('status', 1)])
    db.alerts.create_index([('score_risk', -1)])
    
    print("Index MongoDB créés avec succès (logs, alerts)")

def init_sql_db(app):
    """Initialise la base SQL pour les users"""
    from models.user import User
    with app.app_context():
        db.create_all()
        print("Base de données SQL créée avec succès (users)")

def test_redis_connection():
    """Test la connexion Redis"""
    try:
        redis_client.ping()
        print("Connexion Redis établie avec succès")
        return True
    except redis.ConnectionError:
        print("ERREUR: Redis non disponible. Installez Redis:")
        print("   Windows: https://github.com/microsoftarchive/redis/releases")
        print("   Ou utilisez Docker: docker compose up -d   (voir docker-compose.yml)")
        return False