from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models.alert import Alert
from services.export_service import ExportService
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@alerts_bp.route('/')
@login_required
def list_alerts():
    page = int(request.args.get('page', 1))
    per_page = 50
    skip = (page - 1) * per_page
    
    alerts = Alert.find_all(limit=per_page, skip=skip)
    total = Alert.count()
    
    return render_template('alerts.html', 
                         alerts=alerts, 
                         page=page, 
                         total=total,
                         per_page=per_page)

@alerts_bp.route('/<alert_id>/update', methods=['POST'])
@login_required
def update_alert(alert_id):
    status = request.form.get('status')
    analyst_notes = request.form.get('analyst_notes', '')
    
    update_data = {
        'status': status,
        'analyst_notes': analyst_notes
    }
    
    Alert.update(alert_id, update_data)
    flash('Alerte mise à jour', 'success')
    return redirect(url_for('alerts.list_alerts'))

@alerts_bp.route('/<alert_id>/delete', methods=['POST'])
@login_required
def delete_alert(alert_id):
    Alert.delete(alert_id)
    flash('Alerte supprimée', 'info')
    return redirect(url_for('alerts.list_alerts'))

@alerts_bp.route('/export/json')
@login_required
def export_json():
    alerts = Alert.find_all(limit=1000)
    json_data = ExportService.export_alerts_json(alerts)
    
    from io import BytesIO
    buffer = BytesIO(json_data.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

@alerts_bp.route('/export/pdf')
@login_required
def export_pdf():
    alerts = Alert.find_all(limit=100)
    filename = f'alerts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    ExportService.export_alerts_pdf(alerts, filename)
    
    return send_file(
        filename,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )