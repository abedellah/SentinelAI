# routes/users.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user import User
from config.config import db

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
def list_users():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard.index'))
    
    users = User.find_all()
    return render_template('users.html', users=users)

@users_bp.route('/create', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard.index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'analyst')
    
    if User.find_by_username(username):
        flash('Utilisateur déjà existant', 'warning')
    else:
        User.create(username, password, role)
        flash('Utilisateur créé avec succès', 'success')
    
    return redirect(url_for('users.list_users'))

@users_bp.route('/<user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if str(current_user.id) == str(user_id):
        flash('Impossible de supprimer votre propre compte', 'danger')
    else:
        User.delete(user_id)
        flash('Utilisateur supprimé', 'info')
    
    return redirect(url_for('users.list_users'))