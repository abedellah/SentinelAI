from flask import Blueprint, jsonify, request
from flask_login import login_required
from models.log import Log
from models.alert import Alert
from ml.predict import get_predictor
from services.ids_pipeline import IDSPipeline
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    limit = int(request.args.get('limit', 100))
    logs = Log.find_all(limit=limit)
    
    # Conversion pour JSON
    from services.export_service import ExportService
    serializable = ExportService.to_json_serializable(logs)
    
    return jsonify({
        'total': len(serializable),
        'logs': serializable
    })

@api_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    limit = int(request.args.get('limit', 100))
    alerts = Alert.find_all(limit=limit)
    
    from services.export_service import ExportService
    serializable = ExportService.to_json_serializable(alerts)
    
    return jsonify({
        'total': len(serializable),
        'alerts': serializable
    })

@api_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        predictor = get_predictor()
        result = predictor.predict(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/logs/ingest', methods=['POST'])
@login_required
def ingest_log():
    """API pour ingestion de logs avec pipeline complet"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        result = IDSPipeline.process_log(data)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/retrain', methods=['POST'])
@login_required
def retrain_model():
    """Réentraînement manuel du modèle"""
    try:
        from ml.train_model import train_model
        model, encoder, accuracy = train_model()
        
        return jsonify({
            'success': True,
            'accuracy': float(accuracy),
            'classes': len(encoder.classes_)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500