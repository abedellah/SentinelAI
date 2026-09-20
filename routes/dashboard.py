from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.log import Log
from models.alert import Alert
from collections import Counter

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Statistiques globales
    total_logs = Log.count()
    total_alerts = Alert.count()
    open_alerts = Alert.count_by_status('open')
    high_risk_alerts = len(Alert.find_high_risk(7.0))
    
    # Récupération des derniers logs et alertes
    recent_logs = Log.find_all(limit=10)
    recent_alerts = Alert.find_all(limit=10)
    
    context = {
        'username': current_user.username,
        'role': current_user.role,
        'stats': {
            'total_logs': total_logs,
            'total_alerts': total_alerts,
            'open_alerts': open_alerts,
            'high_risk_alerts': high_risk_alerts
        },
        'recent_logs': recent_logs,
        'recent_alerts': recent_alerts
    }
    
    return render_template('dashboard.html', **context)

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API pour les statistiques du dashboard"""
    
    # Distribution des labels
    all_logs = Log.find_all(limit=1000)
    labels = [log.get('Label', 'BENIGN') for log in all_logs]
    label_counts = Counter(labels)
    
    # Distribution des alertes par type
    all_alerts = Alert.find_all(limit=500)
    alert_types = [alert.get('alert_type', 'unknown') for alert in all_alerts]
    alert_counts = Counter(alert_types)
    
    # Alertes par statut
    status_counts = {
        'open': Alert.count_by_status('open'),
        'closed': Alert.count_by_status('closed'),
        'investigating': Alert.count_by_status('investigating')
    }
    
    return jsonify({
        'label_distribution': dict(label_counts),
        'alert_distribution': dict(alert_counts),
        'status_distribution': status_counts,
        'total_logs': Log.count(),
        'total_alerts': Alert.count()
    })