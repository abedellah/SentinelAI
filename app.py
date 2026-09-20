from flask import Flask, redirect, url_for, session, request
from flask_login import LoginManager
from config.config import Config, db, init_mongo_indexes, init_sql_db, test_redis_connection
from models.user import User
from services.redis_session import RedisSessionManager
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.logs import logs_bp
from routes.alerts import alerts_bp
from routes.users import users_bp
from routes.api import api_bp

# Initialisation Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation SQLAlchemy pour users
db.init_app(app)

# Test connexion Redis
if not test_redis_connection():
    print("⚠️  WARNING: Redis non disponible. Les sessions ne fonctionneront pas.")

# Initialisation bases de données
with app.app_context():
    init_sql_db(app)  # SQL pour users
    init_mongo_indexes()  # MongoDB pour logs et alerts

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)

# Middleware de vérification session Redis
@app.before_request
def verify_redis_session():
    """Vérifie la session Redis pour toutes les routes protégées"""
    
    # Routes publiques (pas de vérification)
    public_routes = ['auth.login', 'auth.logout', 'static']
    
    if request.endpoint in public_routes:
        return
    
    # Si route protégée et utilisateur connecté
    if request.endpoint and hasattr(request, 'url_rule'):
        # Vérifier si session Redis existe
        redis_session_id = session.get('redis_session_id')
        
        if redis_session_id:
            # Vérifier validité session
            if RedisSessionManager.verify_session(redis_session_id):
                # Renouveler TTL à chaque activité
                RedisSessionManager.update_activity(redis_session_id)
            else:
                # Session expirée
                session.pop('redis_session_id', None)
                from flask_login import logout_user
                logout_user()
                from flask import flash
                flash('Session expirée. Veuillez vous reconnecter.', 'warning')
                return redirect(url_for('auth.login'))

# Enregistrement des blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(logs_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(users_bp)
app.register_blueprint(api_bp)

# Route racine
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    print("="*60)
    print("🚀 SentinelAI - Système de Détection d'Intrusions")
    print("="*60)
    print(f"📍 URL: http://{Config.HOST}:{Config.PORT}")
    print(f"🔐 Login: admin / admin123")
    print("="*60)
    print("💾 Architecture Hybride:")
    print(f"   - Users: SQL ({Config.SQLALCHEMY_DATABASE_URI})")
    print(f"   - Logs & Alerts: MongoDB ({Config.MONGO_URI})")
    print(f"   - Sessions: Redis (localhost:6379, TTL: {Config.SESSION_TTL}s)")
    print("="*60)
    print("🔒 Gestion Sessions:")
    print("   - Users: Accès à LEURS sessions uniquement")
    print("   - Admin: Accès à TOUTES les sessions (supervision)")
    print("="*60)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )