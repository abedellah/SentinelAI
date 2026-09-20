import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Chemins
DATASET_PATH = r'C:\Users\oussa\Desktop\MachineLearningCSV\final_dataset.csv'
MODEL_PATH = r'C:\Users\oussa\Desktop\SentinelAI\ml\model.pkl'

# Labels attendus (15 classes)
EXPECTED_LABELS = [
    'DoS Hulk', 'PortScan', 'DDoS', 'BENIGN', 'DoS GoldenEye', 
    'FTP-Patator', 'Bot', 'DoS slowloris', 'SSH-Patator', 
    'Web Attack - Brute Force', 'DoS Slowhttptest', 'Web Attack - XSS', 
    'Infiltration', 'Web Attack - Sql Injection', 'Heartbleed'
]

def preprocess_data(df):
    """Prétraitement des données"""
    print("📊 Prétraitement des données...")
    
    # Sélection des colonnes obligatoires
    required_cols = ['destination_port', 'flow_duration', 'flow_bytes_per_second', 
                     'flow_packets_per_second', 'Label']
    
    # Vérification des colonnes
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Colonne manquante : {col}")
    
    df = df[required_cols].copy()
    
    # Nettoyage
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    
    # Filtrer uniquement les labels attendus
    df = df[df['Label'].isin(EXPECTED_LABELS)]
    
    print(f"✓ Données nettoyées : {len(df)} lignes")
    print(f"✓ Distribution des labels :")
    print(df['Label'].value_counts())
    
    return df

def train_model():
    """Entraînement du modèle RandomForest"""
    print("🚀 Démarrage de l'entraînement du modèle...")
    
    # Chargement du dataset
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset introuvable : {DATASET_PATH}")
    
    print(f"📂 Chargement du dataset : {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    print(f"✓ Dataset chargé : {len(df)} lignes, {len(df.columns)} colonnes")
    
    # Prétraitement
    df = preprocess_data(df)
    
    # Séparation features / labels
    X = df[['destination_port', 'flow_duration', 'flow_bytes_per_second', 'flow_packets_per_second']]
    y = df['Label']
    
    # Encodage des labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split train/test (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"✓ Train : {len(X_train)} lignes | Test : {len(X_test)} lignes")
    
    # Entraînement RandomForest
    print("🌲 Entraînement du RandomForest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    rf_model.fit(X_train, y_train)
    print("✓ Modèle entraîné")
    
    # Évaluation
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n📈 Accuracy : {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\n📊 Rapport de classification :")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # Sauvegarde du modèle + encoder
    model_data = {
        'model': rf_model,
        'label_encoder': label_encoder,
        'feature_names': ['destination_port', 'flow_duration', 'flow_bytes_per_second', 'flow_packets_per_second']
    }
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model_data, MODEL_PATH)
    print(f"\n✅ Modèle sauvegardé : {MODEL_PATH}")
    
    return rf_model, label_encoder, accuracy

if __name__ == '__main__':
    try:
        model, encoder, acc = train_model()
        print("\n" + "="*60)
        print(f"✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
        print(f"   Accuracy : {acc*100:.2f}%")
        print(f"   Classes : {len(encoder.classes_)}")
        print("="*60)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()