from datetime import datetime, timedelta
import random
from config.config import get_mongo_db, db
from models.user import User
from models.log import Log
from models.alert import Alert
from flask import Flask
from config.config import Config

def generate_demo_data():
    """Génère des données de démonstration"""
    print("Génération des données de démonstration...")
    
    # Initialisation Flask pour SQLAlchemy
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Création tables SQL
        db.create_all()
        
        # Nettoyage des bases
        print("Nettoyage des bases de données...")
        
        # Nettoyage MongoDB (logs, alerts)
        mongo_db = get_mongo_db()
        mongo_db.logs.delete_many({})
        mongo_db.alerts.delete_many({})
        print("Collections MongoDB nettoyées (logs, alerts)")
        
        # Nettoyage SQL (users)
        User.query.delete()
        db.session.commit()
        print("Table SQL nettoyée (users)")
        
        # 1. Créer utilisateurs dans SQL
        print("\nCréation des utilisateurs (SQL)...")
        admin_id = User.create('admin', 'admin', 'admin')
        print(f"Admin créé : admin / admin (ID: {admin_id})")
        
        analyst_id = User.create('abdellah', 'abdellah', 'analyst')
        print(f"Analyste créé : abdellah / abdellah (ID: {analyst_id})")
        
        # 2. Générer des logs dans MongoDB
        print("\nGénération des logs (MongoDB)...")
        attack_types = [
            'BENIGN', 'DoS Hulk', 'PortScan', 'DDoS', 'DoS GoldenEye',
            'FTP-Patator', 'Bot', 'DoS slowloris', 'SSH-Patator',
            'Web Attack - Brute Force', 'DoS Slowhttptest', 'Web Attack - XSS',
            'Infiltration', 'Web Attack - Sql Injection', 'Heartbleed'
        ]
        
        protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']
        
        log_ids = []
        for i in range(100):
            label = random.choice(attack_types)
            
            log_data = {
                'timestamp': datetime.utcnow() - timedelta(hours=random.randint(0, 72)),
                'source_ip': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'destination_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'source_port': random.randint(1024, 65535),
                'destination_port': random.choice([80, 443, 22, 21, 3306, 8080]),
                'protocol': random.choice(protocols),
                'event_type': 'network',
                'status': 'processed',
                'flow_duration': random.randint(0, 10000),
                'flow_bytes_per_second': random.uniform(0, 500000),
                'flow_packets_per_second': random.uniform(0, 5000),
                'Label': label,
                'notes': f'Log de démonstration {i+1}',
                'attack_name': label if label != 'BENIGN' else '',
                'description': f'Activité détectée: {label}',
                'severity_level': 'high' if label in ['DDoS', 'Infiltration', 'Heartbleed'] else 'medium' if label != 'BENIGN' else 'low'
            }
            
            log_id = Log.create(log_data)
            log_ids.append(log_id)
        
        print(f"{len(log_ids)} logs créés")
        
        # 3. Générer des alertes dans MongoDB (avec user_id SQL)
        print("\nGénération des alertes (MongoDB avec référence SQL)...")
        alert_count = 0
        for log_id in log_ids:
            log = Log.find_by_id(log_id)
            if log['Label'] != 'BENIGN' and random.random() > 0.3:
                
                risk_scores = {
                    'Heartbleed': 10.0,
                    'Infiltration': 9.5,
                    'DDoS': 9.0,
                    'Web Attack - Sql Injection': 8.5,
                    'DoS Hulk': 8.0,
                    'Bot': 8.0,
                    'Web Attack - XSS': 7.5,
                    'DoS slowloris': 7.5,
                    'DoS Slowhttptest': 7.5,
                    'Web Attack - Brute Force': 7.0,
                    'SSH-Patator': 6.5,
                    'FTP-Patator': 6.0,
                    'PortScan': 3.0
                }
                
                alert_data = {
                    'log_id': str(log_id),
                    'timestamp': log['timestamp'],
                    'alert_type': log['Label'],
                    'description': f"Activité suspecte détectée : {log['Label']}",
                    'score_risk': risk_scores.get(log['Label'], 5.0),
                    'status': random.choice(['open', 'investigating', 'closed']),
                    'analyst_notes': f'Alerte générée automatiquement pour {log["Label"]}',
                    'user_id': str(analyst_id)  # Référence SQL user ID
                }
                
                Alert.create(alert_data)
                alert_count += 1
        
        print(f"{alert_count} alertes créées")
        
        print("\n" + "="*60)
        print("DONNÉES DE DÉMONSTRATION GÉNÉRÉES AVEC SUCCÈS")
        print("="*60)
        print(f"   Users (SQL): 2 (admin, analyst)")
        print(f"   Logs (MongoDB): {len(log_ids)}")
        print(f"   Alerts (MongoDB): {alert_count}")
        print("="*60)
        print("\nArchitecture hybride:")
        print(f"   - Users: SQLite ({Config.SQLALCHEMY_DATABASE_URI})")
        print(f"   - Logs & Alerts: MongoDB ({Config.MONGO_URI})")
        print("="*60)

if __name__ == '__main__':
    try:
        generate_demo_data()
    except Exception as e:
        print(f"\nERREUR : {e}")
        import traceback
        traceback.print_exc()