from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from services.redis_session import RedisSessionManager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.verify_password(username, password):
            user = User.find_by_username(username)
            
            # Login Flask-Login (gère les cookies)
            login_user(user)
            
            # Créer session Redis
            session_id = RedisSessionManager.create_session(
                user_id=user.id,
                username=user.username,
                role=user.role,
                ip_address=request.remote_addr
            )
            
            # Stocker session_id dans Flask session (cookie)
            session['redis_session_id'] = session_id
            
            # Mise à jour last_login SQL
            User.update_last_login(user.id, request.remote_addr)
            
            flash(f'Connexion réussie. Session: {session_id[:8]}...', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Identifiants incorrects', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Récupérer session_id
    session_id = session.get('redis_session_id')
    
    # Supprimer session Redis
    if session_id:
        RedisSessionManager.delete_session(session_id)
        session.pop('redis_session_id', None)
    
    # Logout Flask-Login
    logout_user()
    
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/sessions')
@login_required
def view_sessions():
    """Vue pour voir ses sessions actives (user) ou toutes (admin)"""
    
    if current_user.role == 'admin':
        # Admin : voir TOUTES les sessions
        all_sessions = RedisSessionManager.get_all_sessions()
        sessions_by_user = RedisSessionManager.get_sessions_by_user()
        statistics = RedisSessionManager.get_statistics()
        
        return render_template('admin_sessions.html',
                             all_sessions=all_sessions,
                             sessions_by_user=sessions_by_user,
                             statistics=statistics,
                             current_session_id=session.get('redis_session_id'))
    else:
        # User normal : voir UNIQUEMENT ses sessions
        sessions = RedisSessionManager.get_user_sessions(current_user.id)
        current_session_id = session.get('redis_session_id')
        
        return render_template('sessions.html', 
                             sessions=sessions, 
                             current_session_id=current_session_id)

@auth_bp.route('/sessions/<session_id>/revoke', methods=['POST'])
@login_required
def revoke_session(session_id):
    """Révoquer une session spécifique"""
    session_data = RedisSessionManager.get_session(session_id)
    
    if not session_data:
        flash('Session introuvable ou déjà expirée', 'warning')
        return redirect(url_for('auth.view_sessions'))
    
    # Vérifier les permissions
    if current_user.role == 'admin':
        # Admin peut révoquer n'importe quelle session
        result = RedisSessionManager.force_delete_session_admin(session_id, current_user.id)
        if result['success']:
            flash(f"{result['message']}", 'success')
        else:
            flash(result['message'], 'danger')
    else:
        # User normal peut révoquer UNIQUEMENT ses propres sessions
        if session_data.get('user_id') == current_user.id:
            RedisSessionManager.delete_session(session_id)
            flash('Session révoquée avec succès', 'success')
        else:
            flash('Accès refusé : cette session ne vous appartient pas', 'danger')
    
    return redirect(url_for('auth.view_sessions'))

@auth_bp.route('/sessions/revoke-all', methods=['POST'])
@login_required
def revoke_all_sessions():
    """Révoquer toutes ses sessions (sauf la courante)"""
    current_session_id = session.get('redis_session_id')
    sessions = RedisSessionManager.get_user_sessions(current_user.id)
    
    count = 0
    for sess in sessions:
        if sess.get('session_id') != current_session_id:
            RedisSessionManager.delete_session(sess.get('session_id'))
            count += 1
    
    flash(f'{count} session(s) révoquée(s)', 'success')
    return redirect(url_for('auth.view_sessions'))