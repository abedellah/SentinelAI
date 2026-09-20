import os
import secrets
from pymongo import MongoClient
from flask_sqlalchemy import SQLAlchemy
import redis

# Instance SQLAlchemy pour les users
db = SQLAlchemy()

# Instance Redis pour les sessions
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)  # set SECRET_KEY in production
    
    # MongoDB Configuration (pour logs et alerts)
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB = 'sentinelai_db'
    
    # Collections MongoDB
    LOGS_COLLECTION = 'logs'
    ALERTS_COLLECTION = 'alerts'
    
    # PostgreSQL Configuration (pour users)
    # Option 1: PostgreSQL (recommandé en production)
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/sentinelai_users'
    
    # Option 2: SQLite (simple, pour développement)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/oussa/Desktop/SentinelAI/sentinelai_users.db'
    
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
    MODEL_PATH = r'C:\Users\oussa\Desktop\SentinelAI\ml\model.pkl'
    DATASET_PATH = r'C:\Users\oussa\Desktop\MachineLearningCSV\final_dataset.csv'
    
    # Flask
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000

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
        print("   Ou utilisez Docker: docker run -d -p 6379:6379 redis")
        return False