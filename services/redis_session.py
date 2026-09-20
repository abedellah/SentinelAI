"""
Service de gestion des sessions Redis
Gère le cycle de vie complet des sessions utilisateur
"""

import uuid
import json
from datetime import datetime, timedelta
from config.config import redis_client, Config

class RedisSessionManager:
    """Gestionnaire de sessions Redis"""
    
    @staticmethod
    def create_session(user_id, username, role, ip_address):
        """
        Crée une nouvelle session Redis après login
        
        Args:
            user_id: ID utilisateur SQL
            username: Nom d'utilisateur
            role: Rôle (admin/analyst)
            ip_address: IP de connexion
            
        Returns:
            session_id: ID unique de la session
        """
        # Génération d'un ID de session unique
        session_id = str(uuid.uuid4())
        
        # Clé Redis
        session_key = f"sentinelai:session:{session_id}"
        
        # Données de session
        session_data = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'ip_address': ip_address,
            'login_time': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat()
        }
        
        # Stockage dans Redis avec TTL
        redis_client.setex(
            session_key,
            Config.SESSION_TTL,
            json.dumps(session_data)
        )
        
        # Ajouter à la liste des sessions actives de l'utilisateur
        user_sessions_key = f"sentinelai:user:{user_id}:sessions"
        redis_client.sadd(user_sessions_key, session_id)
        redis_client.expire(user_sessions_key, Config.SESSION_TTL)
        
        print(f"Session créée: {session_id} pour user {username} (TTL: {Config.SESSION_TTL}s)")
        
        return session_id
    
    @staticmethod
    def get_session(session_id):
        """
        Récupère les données d'une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            dict: Données de session ou None
        """
        if not session_id:
            return None
        
        session_key = f"sentinelai:session:{session_id}"
        session_data = redis_client.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        
        return None
    
    @staticmethod
    def verify_session(session_id):
        """
        Vérifie si une session est valide
        
        Args:
            session_id: ID de la session
            
        Returns:
            bool: True si session valide
        """
        session_key = f"sentinelai:session:{session_id}"
        return redis_client.exists(session_key) > 0
    
    @staticmethod
    def update_activity(session_id):
        """
        Met à jour la dernière activité et renouvelle le TTL
        
        Args:
            session_id: ID de la session
        """
        session_data = RedisSessionManager.get_session(session_id)
        
        if session_data:
            # Mise à jour dernière activité
            session_data['last_activity'] = datetime.utcnow().isoformat()
            
            session_key = f"sentinelai:session:{session_id}"
            
            # Renouvellement du TTL
            redis_client.setex(
                session_key,
                Config.SESSION_TTL,
                json.dumps(session_data)
            )
    
    @staticmethod
    def delete_session(session_id):
        """
        Supprime une session (logout)
        
        Args:
            session_id: ID de la session
            
        Returns:
            bool: True si supprimée
        """
        if not session_id:
            return False
        
        # Récupérer user_id avant suppression
        session_data = RedisSessionManager.get_session(session_id)
        
        if session_data:
            user_id = session_data.get('user_id')
            
            # Supprimer la session
            session_key = f"sentinelai:session:{session_id}"
            redis_client.delete(session_key)
            
            # Retirer de la liste des sessions utilisateur
            if user_id:
                user_sessions_key = f"sentinelai:user:{user_id}:sessions"
                redis_client.srem(user_sessions_key, session_id)
            
            print(f"Session supprimée: {session_id}")
            return True
        
        return False
    
    @staticmethod
    def get_user_sessions(user_id):
        """
        Récupère toutes les sessions actives d'un utilisateur
        
        Args:
            user_id: ID utilisateur SQL
            
        Returns:
            list: Liste des sessions actives
        """
        user_sessions_key = f"sentinelai:user:{user_id}:sessions"
        session_ids = redis_client.smembers(user_sessions_key)
        
        sessions = []
        for session_id in session_ids:
            session_data = RedisSessionManager.get_session(session_id)
            if session_data:
                session_data['session_id'] = session_id
                sessions.append(session_data)
            else:
                # Nettoyer référence orpheline
                redis_client.srem(user_sessions_key, session_id)
        
        return sessions
    
    @staticmethod
    def get_all_sessions():
        """
        Récupère TOUTES les sessions actives (admin uniquement)
        
        Returns:
            list: Liste de toutes les sessions avec détails
        """
        pattern = "sentinelai:session:*"
        session_keys = redis_client.keys(pattern)
        
        all_sessions = []
        for session_key in session_keys:
            session_id = session_key.replace('sentinelai:session:', '')
            session_data = RedisSessionManager.get_session(session_id)
            
            if session_data:
                session_data['session_id'] = session_id
                
                # Ajouter TTL
                ttl = redis_client.ttl(session_key)
                session_data['ttl_seconds'] = ttl
                session_data['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=ttl)
                ).isoformat() if ttl > 0 else None
                
                all_sessions.append(session_data)
        
        # Trier par dernière activité (plus récent d'abord)
        all_sessions.sort(
            key=lambda x: x.get('last_activity', ''), 
            reverse=True
        )
        
        return all_sessions
    
    @staticmethod
    def delete_all_user_sessions(user_id):
        """
        Supprime toutes les sessions d'un utilisateur
        
        Args:
            user_id: ID utilisateur SQL
            
        Returns:
            int: Nombre de sessions supprimées
        """
        sessions = RedisSessionManager.get_user_sessions(user_id)
        count = 0
        
        for session in sessions:
            if RedisSessionManager.delete_session(session.get('session_id')):
                count += 1
        
        return count
    
    @staticmethod
    def force_delete_session_admin(session_id, admin_user_id):
        """
        Supprime n'importe quelle session (admin uniquement)
        
        Args:
            session_id: ID de la session à supprimer
            admin_user_id: ID de l'admin qui effectue l'action
            
        Returns:
            dict: Résultat avec détails
        """
        session_data = RedisSessionManager.get_session(session_id)
        
        if not session_data:
            return {
                'success': False,
                'message': 'Session introuvable ou déjà expirée'
            }
        
        target_username = session_data.get('username')
        
        # Supprimer la session
        if RedisSessionManager.delete_session(session_id):
            return {
                'success': True,
                'message': f'Session de {target_username} révoquée par admin',
                'target_user': target_username
            }
        
        return {
            'success': False,
            'message': 'Erreur lors de la suppression'
        }
    
    @staticmethod
    def get_active_sessions_count():
        """
        Compte le nombre total de sessions actives
        
        Returns:
            int: Nombre de sessions actives
        """
        pattern = "sentinelai:session:*"
        sessions = redis_client.keys(pattern)
        return len(sessions)
    
    @staticmethod
    def get_sessions_by_user():
        """
        Regroupe les sessions par utilisateur (admin uniquement)
        
        Returns:
            dict: {user_id: [sessions]}
        """
        all_sessions = RedisSessionManager.get_all_sessions()
        
        sessions_by_user = {}
        for session in all_sessions:
            user_id = session.get('user_id')
            if user_id not in sessions_by_user:
                sessions_by_user[user_id] = []
            sessions_by_user[user_id].append(session)
        
        return sessions_by_user
    
    @staticmethod
    def get_session_info(session_id):
        """
        Récupère les informations détaillées d'une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            dict: Infos complètes avec TTL
        """
        session_data = RedisSessionManager.get_session(session_id)
        
        if session_data:
            session_key = f"sentinelai:session:{session_id}"
            ttl = redis_client.ttl(session_key)
            
            session_data['ttl_seconds'] = ttl
            session_data['expires_at'] = (
                datetime.utcnow() + timedelta(seconds=ttl)
            ).isoformat() if ttl > 0 else None
            
            return session_data
        
        return None
    
    @staticmethod
    def get_statistics():
        """
        Statistiques globales des sessions (admin uniquement)
        
        Returns:
            dict: Statistiques complètes
        """
        all_sessions = RedisSessionManager.get_all_sessions()
        sessions_by_user = RedisSessionManager.get_sessions_by_user()
        
        # Compter par rôle
        roles = {}
        for session in all_sessions:
            role = session.get('role', 'unknown')
            roles[role] = roles.get(role, 0) + 1
        
        # Compter par IP
        ips = {}
        for session in all_sessions:
            ip = session.get('ip_address', 'unknown')
            ips[ip] = ips.get(ip, 0) + 1
        
        return {
            'total_sessions': len(all_sessions),
            'total_users': len(sessions_by_user),
            'sessions_by_role': roles,
            'sessions_by_ip': ips,
            'avg_sessions_per_user': round(len(all_sessions) / max(len(sessions_by_user), 1), 2)
        }