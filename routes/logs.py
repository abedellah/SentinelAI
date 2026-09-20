from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from models.log import Log
from services.ids_pipeline import IDSPipeline
from services.export_service import ExportService
from datetime import datetime
import pandas as pd
import os
from werkzeug.utils import secure_filename

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

UPLOAD_FOLDER = r'C:\Users\oussa\Desktop\SentinelAI\uploads'
ALLOWED_EXTENSIONS = {'csv'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@logs_bp.route('/')
@login_required
def list_logs():
    page = int(request.args.get('page', 1))
    per_page = 50
    skip = (page - 1) * per_page
    
    logs = Log.find_all(limit=per_page, skip=skip)
    total = Log.count()
    
    return render_template('logs.html', 
                         logs=logs, 
                         page=page, 
                         total=total,
                         per_page=per_page)

@logs_bp.route('/create', methods=['POST'])
@login_required
def create_log():
    raw_log = {
        'source_ip': request.form.get('source_ip'),
        'destination_ip': request.form.get('destination_ip'),
        'source_port': int(request.form.get('source_port', 0)),
        'destination_port': int(request.form.get('destination_port', 0)),
        'protocol': request.form.get('protocol', 'TCP'),
        'event_type': request.form.get('event_type', 'network'),
        'flow_duration': int(request.form.get('flow_duration', 0)),
        'flow_bytes_per_second': float(request.form.get('flow_bytes_per_second', 0)),
        'flow_packets_per_second': float(request.form.get('flow_packets_per_second', 0)),
        'Label': request.form.get('Label', 'BENIGN'),
        'notes': request.form.get('notes', ''),
        'timestamp': datetime.utcnow()
    }
    
    result = IDSPipeline.process_log(raw_log, user_id=str(current_user.id))
    
    flash(f'Log créé avec succès. Prédiction: {result["predicted_label"]} (Score: {result["risk_score"]})', 'success')
    return redirect(url_for('logs.list_logs'))

@logs_bp.route('/import', methods=['POST'])
@login_required
def import_csv():
    """Importer un fichier CSV avec plusieurs logs"""
    if 'csv_file' not in request.files:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('logs.list_logs'))
    
    file = request.files['csv_file']
    
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('logs.list_logs'))
    
    if not allowed_file(file.filename):
        flash('Format de fichier invalide. Utilisez un fichier CSV', 'danger')
        return redirect(url_for('logs.list_logs'))
    
    try:
        # Sauvegarde temporaire
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Lecture du CSV
        df = pd.read_csv(filepath)
        
        # Colonnes requises
        required_cols = ['destination_port', 'flow_duration', 'flow_bytes_per_second', 'flow_packets_per_second']
        optional_cols = ['source_ip', 'destination_ip', 'source_port', 'protocol', 'event_type', 'Label']
        
        # Vérification colonnes obligatoires
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            flash(f'Colonnes manquantes dans le CSV: {", ".join(missing_cols)}', 'danger')
            os.remove(filepath)
            return redirect(url_for('logs.list_logs'))
        
        # Traitement des logs
        success_count = 0
        error_count = 0
        alert_count = 0
        
        for idx, row in df.iterrows():
            try:
                raw_log = {
                    'source_ip': str(row.get('source_ip', f'192.168.1.{idx % 255 + 1}')),
                    'destination_ip': str(row.get('destination_ip', f'10.0.0.{idx % 255 + 1}')),
                    'source_port': int(row.get('source_port', 0)),
                    'destination_port': int(row['destination_port']),
                    'protocol': str(row.get('protocol', 'TCP')),
                    'event_type': str(row.get('event_type', 'network')),
                    'flow_duration': int(row['flow_duration']),
                    'flow_bytes_per_second': float(row['flow_bytes_per_second']),
                    'flow_packets_per_second': float(row['flow_packets_per_second']),
                    'Label': str(row.get('Label', 'BENIGN')),
                    'notes': f'Importé depuis CSV: {filename}',
                    'timestamp': datetime.utcnow()
                }
                
                # Traitement via pipeline IDS
                result = IDSPipeline.process_log(raw_log, user_id=str(current_user.id))
                success_count += 1
                
                if result.get('alert_created'):
                    alert_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Erreur ligne {idx}: {e}")
        
        # Suppression du fichier temporaire
        os.remove(filepath)
        
        # Message de confirmation
        msg = f'Import terminé: {success_count} logs importés'
        if alert_count > 0:
            msg += f', {alert_count} alertes créées'
        if error_count > 0:
            msg += f', {error_count} erreurs'
        
        flash(msg, 'success' if error_count == 0 else 'warning')
        
    except Exception as e:
        flash(f'Erreur lors de l\'import: {str(e)}', 'danger')
        if os.path.exists(filepath):
            os.remove(filepath)
    
    return redirect(url_for('logs.list_logs'))

@logs_bp.route('/<log_id>/delete', methods=['POST'])
@login_required
def delete_log(log_id):
    Log.delete(log_id)
    flash('Log supprimé', 'info')
    return redirect(url_for('logs.list_logs'))

@logs_bp.route('/export/json')
@login_required
def export_json():
    logs = Log.find_all(limit=1000)
    json_data = ExportService.export_logs_json(logs)
    
    from io import BytesIO
    buffer = BytesIO(json_data.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

@logs_bp.route('/export/pdf')
@login_required
def export_pdf():
    logs = Log.find_all(limit=100)
    filename = f'logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    ExportService.export_logs_pdf(logs, filename)
    
    return send_file(
        filename,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )