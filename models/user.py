# models/user.py
from datetime import datetime
from config.config import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.LargeBinary, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='analyst')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Sessions stockées en JSON
    recent_sessions = db.Column(db.JSON, default=list)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @staticmethod
    def create(username, password, role='analyst'):
        """Crée un nouvel utilisateur"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            recent_sessions=[]
        )
        db.session.add(user)
        db.session.commit()
        return user.id
    
    @staticmethod
    def find_by_username(username):
        """Trouve un user par username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_id(user_id):
        """Trouve un user par ID"""
        return User.query.get(int(user_id))
    
    @staticmethod
    def verify_password(username, password):
        """Vérifie le mot de passe"""
        user = User.find_by_username(username)
        if user:
            return bcrypt.checkpw(password.encode('utf-8'), user.password_hash)
        return False
    
    @staticmethod
    def update_last_login(user_id, ip_address):
        """Met à jour la dernière connexion"""
        user = User.query.get(int(user_id))
        if user:
            session = {
                'login_time': datetime.utcnow().isoformat(),
                'logout_time': None,
                'ip_address': ip_address
            }
            
            # Récupération sessions existantes
            sessions = user.recent_sessions if user.recent_sessions else []
            sessions.append(session)
            
            # Garder seulement les 10 dernières
            user.recent_sessions = sessions[-10:]
            user.last_login = datetime.utcnow()
            
            db.session.commit()
    
    @staticmethod
    def find_all():
        """Liste tous les users"""
        return User.query.all()
    
    @staticmethod
    def delete(user_id):
        """Supprime un user"""
        user = User.query.get(int(user_id))
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    # Méthodes Flask-Login
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)