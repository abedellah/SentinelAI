# services/ids_pipeline.py
from datetime import datetime
from models.log import Log
from models.alert import Alert
from ml.predict import get_predictor
from .risk_scoring import RiskScorer

class IDSPipeline:
    """Pipeline IDS complet : normalisation → insertion → ML → alertes"""
    
    @staticmethod
    def normalize_log(raw_log):
        """Normalise un log brut"""
        normalized = {
            'timestamp': raw_log.get('timestamp', datetime.utcnow()),
            'source_ip': str(raw_log.get('source_ip', 'unknown')),
            'destination_ip': str(raw_log.get('destination_ip', 'unknown')),
            'source_port': int(raw_log.get('source_port', 0)),
            'destination_port': int(raw_log.get('destination_port', 0)),
            'protocol': str(raw_log.get('protocol', 'TCP')),
            'event_type': str(raw_log.get('event_type', 'network')),
            'status': 'processed',
            'flow_duration': int(raw_log.get('flow_duration', 0)),
            'flow_bytes_per_second': float(raw_log.get('flow_bytes_per_second', 0.0)),
            'flow_packets_per_second': float(raw_log.get('flow_packets_per_second', 0.0)),
            'Label': str(raw_log.get('Label', 'BENIGN')),
            'notes': str(raw_log.get('notes', '')),
            'attack_name': str(raw_log.get('attack_name', '')),
            'description': str(raw_log.get('description', '')),
            'severity_level': str(raw_log.get('severity_level', 'low'))
        }
        return normalized
    
    @staticmethod
    def process_log(raw_log, user_id=None):
        """Pipeline complet : normalisation → insertion → ML → score → alerte"""
        
        # 1. Normalisation
        normalized = IDSPipeline.normalize_log(raw_log)
        
        # 2. Insertion MongoDB
        log_id = Log.create(normalized)
        
        # 3. Classification ML
        try:
            predictor = get_predictor()
            ml_result = predictor.predict({
                'destination_port': normalized['destination_port'],
                'flow_duration': normalized['flow_duration'],
                'flow_bytes_per_second': normalized['flow_bytes_per_second'],
                'flow_packets_per_second': normalized['flow_packets_per_second']
            })
            
            predicted_label = ml_result['label']
            confidence = ml_result['confidence']
            
            # Mise à jour du log avec prédiction
            Log.update(log_id, {'Label': predicted_label})
            
        except Exception as e:
            predicted_label = normalized['Label']
            confidence = 0.0
            print(f"⚠️ Erreur ML : {e}")
        
        # 4. Calcul du score de risque
        risk_score = RiskScorer.calculate_risk(predicted_label, confidence, normalized)
        
        # 5. Création automatique d'alerte si risque élevé
        if risk_score >= 5.0:
            alert_data = {
                'log_id': str(log_id),
                'timestamp': datetime.utcnow(),
                'alert_type': predicted_label,
                'description': f"Activité suspecte détectée : {predicted_label} (Confiance: {confidence:.2f})",
                'score_risk': risk_score,
                'status': 'open',
                'analyst_notes': '',
                'user_id': user_id
            }
            Alert.create(alert_data)
        
        return {
            'log_id': str(log_id),
            'predicted_label': predicted_label,
            'confidence': confidence,
            'risk_score': risk_score,
            'alert_created': risk_score >= 5.0
        }