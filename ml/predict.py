import joblib
import numpy as np
import os

MODEL_PATH = r'C:\Users\oussa\Desktop\SentinelAI\ml\model.pkl'

class MLPredictor:
    def __init__(self):
        self.model_data = None
        self.load_model()
    
    def load_model(self):
        """Charge le modèle ML"""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")
        
        self.model_data = joblib.load(MODEL_PATH)
        print(f"✓ Modèle chargé : {MODEL_PATH}")
    
    def predict(self, features):
        """
        Prédiction sur un log
        features : dict avec destination_port, flow_duration, flow_bytes_per_second, flow_packets_per_second
        """
        if not self.model_data:
            raise ValueError("Modèle non chargé")
        
        model = self.model_data['model']
        label_encoder = self.model_data['label_encoder']
        feature_names = self.model_data['feature_names']
        
        # Extraction des features
        X = np.array([[
            features.get('destination_port', 0),
            features.get('flow_duration', 0),
            features.get('flow_bytes_per_second', 0.0),
            features.get('flow_packets_per_second', 0.0)
        ]])
        
        # Prédiction
        pred_encoded = model.predict(X)[0]
        pred_label = label_encoder.inverse_transform([pred_encoded])[0]
        
        # Probabilités
        probabilities = model.predict_proba(X)[0]
        confidence = float(np.max(probabilities))
        
        return {
            'label': pred_label,
            'confidence': confidence,
            'probabilities': {
                label_encoder.classes_[i]: float(probabilities[i]) 
                for i in range(len(probabilities))
            }
        }
    
    def predict_batch(self, features_list):
        """Prédiction sur plusieurs logs"""
        results = []
        for features in features_list:
            try:
                result = self.predict(features)
                results.append(result)
            except Exception as e:
                results.append({'label': 'ERROR', 'confidence': 0.0, 'error': str(e)})
        return results

# Instance globale
predictor = MLPredictor()

def get_predictor():
    """Retourne l'instance du prédicteur"""
    return predictor