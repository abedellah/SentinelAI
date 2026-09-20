# SentinelAI - Système de Détection d'Intrusions avec Architecture Polyglotte

**SentinelAI est un IDS polyglotte temps réel avec Machine Learning pour détecter automatiquement 15 types d'attaques réseau en utilisant une architecture hybride SQL + MongoDB + Redis.**

## Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Données de test](#données-de-test)
- [Structure du projet](#structure-du-projet)
- [API](#api)
- [Tests](#tests)
- [Dépannage](#dépannage)
- [Auteur](#auteur)

---

## Description

SentinelAI est un système de détection d'intrusions (IDS) avancé qui combine trois technologies de bases de données pour optimiser performance, sécurité et scalabilité :

- **SQL (PostgreSQL/SQLite)** : Gestion sécurisée des utilisateurs avec transactions ACID
- **MongoDB** : Stockage haute performance des logs réseau et alertes
- **Redis** : Cache mémoire pour sessions utilisateur avec TTL automatique

Le système utilise un modèle Machine Learning (RandomForest) pour classifier automatiquement 15 types d'attaques réseau en temps réel.

### Types d'attaques détectés

DoS Hulk • PortScan • DDoS • BENIGN • DoS GoldenEye • FTP-Patator • Bot • DoS slowloris • SSH-Patator • Web Attack - Brute Force • DoS Slowhttptest • Web Attack - XSS • Infiltration • Web Attack - Sql Injection • Heartbleed

---

## Fonctionnalités

# Détection et Analyse
- Import CSV massif (500+ logs/batch)
- Classification ML temps réel (<100ms/log)
- Calcul automatique scores de risque (0-10)
- Génération alertes automatiques (seuil ≥5)

# Dashboard SOC
- Visualisation temps réel (Chart.js)
- Distribution des attaques par type
- Statut des alertes (open/investigating/closed)
- Export PDF et JSON

# Sécurité
- Authentification bcrypt (12 rounds)
- Sessions Redis avec TTL 1h
- Gestion multi-appareils
- Révocation instantanée sessions
- Contrôle d'accès basé rôles (admin/analyst)

# Performance
- MongoDB : 11,700 insertions/seconde
- SQL auth : <10ms
- Redis cache : <5ms
- Prédiction ML : <100ms

---

## Architecture

```
┌─────────────┐
│   Browser   │
│   (HTML5)   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│    Flask    │
│  (Backend)  │
└──┬───┬───┬──┘
   │   │   │
   ▼   ▼   ▼
┌───┐┌───┐┌───┐
│SQL││Mgo││Red│
│   ││DB ││is │
└───┘└───┘└───┘
```

**Répartition des données** :
- **SQL** : users (authentification ACID)
- **MongoDB** : logs + alerts (insertion rapide)
- **Redis** : sessions (TTL automatique)

---

## Prérequis

### Logiciels requis

| Logiciel   | Version minimale |
|------------|------------------|
| Python     | 3.12             |
| pip        | 23.0+            |
| MongoDB    | 5.0+             |
| Redis      | 7.0+             |
| SQLite     | Intégré à Python |

### Bibliothèques Python principales

```
Flask==3.0.0
flask-login==0.6.3
pymongo==4.6.1
bcrypt==4.1.2
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.3
joblib==1.3.2
flask-sqlalchemy==3.1.1
redis==5.0.1
```

---

## Installation

### 1. Cloner le projet

```bash
cd SentinelAI
```

### 2. Créer environnement virtuel

**Windows** :
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installer dépendances Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Installer bases de données

#### MongoDB

**Windows** :
```powershell
# Télécharger : https://www.mongodb.com/try/download/community
# Installer et démarrer service
net start MongoDB
```

**Vérifier** :
```bash
mongo --eval "db.adminCommand('listDatabases')"
```

#### Redis

**Windows (Docker recommandé)** :
```powershell
docker run -d -p 6379:6379 --name redis-sentinel redis:latest
```

**Vérifier** :
```bash
redis-cli ping
# Doit retourner : PONG
```

#### SQLite (par défaut)

SQLite est une base de données légère intégrée à Python, ne nécessitant aucune installation supplémentaire.

---

## Configuration

### config/config.py

**Modifier la connexion SQL** (optionnel) :

```python
# Par défaut : SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/oussa/Desktop/SentinelAI/sentinelai_users.db'
```

**Modifier TTL sessions Redis** (optionnel) :

```python
SESSION_TTL = 3600  # 1 heure 
```

---

## Lancement

### Initialisation bases de données

**1. Créer données de démonstration** :
```bash
python data/demo_data.py
```

**Sortie attendue** :
```
Collections MongoDB nettoyées (logs, alerts)
Table SQL nettoyée (users)
Admin créé : admin / admin123 (ID: 1)
Analyste créé : analyst / analyst123 (ID: 2)
100 logs créés
30 alertes créées
```

**2. Entraîner modèle ML** :
```bash
python ml/train_model.py
```

**Sortie attendue** :
```
Chargement du dataset : C:\...\final_dataset.csv
Dataset chargé : 2830743 lignes
Données nettoyées : 2830743 lignes
Entraînement du RandomForest...
Modèle entraîné
Accuracy : 0.9975 (99.75%)
Modèle sauvegardé : C:\...\model.pkl
```

### Lancer l'application

```bash
python app.py
```

**Sortie attendue** :
```
============================================================
SentinelAI - Système de Détection d'Intrusions
============================================================
 * Running on http://0.0.0.0:5000
```

### Accéder à l'application

**URL** : http://localhost:5000

**Compte par défaut** :

| Username | Password | Rôle | Permissions |
|----------|----------|------|-------------|
| `admin` | `admin` | Administrateur | Toutes (users, sessions globales, ML) |
| `abdellah` | `abdellah` | Analyste | Logs, alertes, ses sessions uniquement |

---

## Scripts d'initialisation des bases

### SQL - database/init_users.sql

```sql
-- Création table users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash BYTEA NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst',
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recent_sessions JSON DEFAULT '[]'
);
```

### MongoDB - database/init_logs.js

```javascript
// Connexion base sentinelai_db
use sentinelai_db;

// Suppression collections existantes
db.logs.drop();
db.alerts.drop();

// Création index logs
db.logs.createIndex({ "timestamp": -1 });
db.logs.createIndex({ "source_ip": 1 });
db.logs.createIndex({ "Label": 1 });
db.logs.createIndex({ "event_type": 1 });

// Création index alerts
db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "log_id": 1 });
db.alerts.createIndex({ "score_risk": -1 });
db.alerts.createIndex({ "status": 1 });

// Insertion logs de test
db.logs.insertMany([
    {
        timestamp: new Date(),
        source_ip: "192.168.1.100",
        destination_ip: "10.0.0.50",
        source_port: 54321,
        destination_port: 80,
        protocol: "TCP",
        event_type: "network",
        status: "processed",
        flow_duration: 5000,
        flow_bytes_per_second: 150000.5,
        flow_packets_per_second: 1500.2,
        Label: "DDoS",
        notes: "Log de test",
        attack_details: {
            attack_name: "DDoS",
            description: "Distributed Denial of Service",
            severity_level: "high"
        }
    }
]);
```

### Redis - database/init_sessions.sh

```bash
#!/bin/bash
# Script de test sessions Redis

echo "Initialisation sessions Redis de test..."

# Session admin
redis-cli SETEX "sentinelai:session:test-admin-uuid" 3600 '{"user_id":1,"username":"admin","role":"admin","ip_address":"127.0.0.1","login_time":"2025-01-15T10:00:00"}'

# Vérification
echo "Sessions créées :"
redis-cli KEYS "sentinelai:session:*"

echo "Sessions Redis créées avec succès"
```

---

## Données de test

### CSV Logs - data/test_logs.csv

**Fichier exemple avec 500+ lignes** :

```csv
destination_port,flow_duration,flow_bytes_per_second,flow_packets_per_second,source_ip,destination_ip,source_port,protocol,event_type,Label
80,5000,150000.5,1500.2,192.168.1.100,10.0.0.50,54321,TCP,network,DDoS
443,3000,8000.3,80.5,192.168.1.101,10.0.0.51,54322,TCP,network,BENIGN
22,10000,50000.8,500.1,192.168.1.102,10.0.0.52,54323,TCP,network,SSH-Patator
```

**Utiliser** :
1. Connectez-vous sur http://localhost:5000
2. Logs → Import CSV
3. Sélectionnez `data/test_logs.csv`
4. Cliquez "Importer"

---

## Structure du projet

```
SentinelAI/
├── app.py                      # Point d'entrée Flask
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
│
├── config/                     # Configuration
│   ├── __init__.py
│   └── config.py              # Config SQL + MongoDB + Redis
│
├── models/                     # Modèles de données
│   ├── __init__.py
│   ├── user.py                # Modèle User (SQL)
│   ├── log.py                 # Modèle Log (MongoDB)
│   └── alert.py               # Modèle Alert (MongoDB)
│
├── routes/                     # Routes Flask
│   ├── __init__.py
│   ├── auth.py                # Authentification + sessions
│   ├── dashboard.py           # Dashboard SOC
│   ├── logs.py                # CRUD logs + import CSV
│   ├── alerts.py              # CRUD alerts
│   ├── users.py               # Gestion users (admin)
│   └── api.py                 # API REST
│
├── services/                   # Services métier
│   ├── __init__.py
│   ├── ids_pipeline.py        # Pipeline IDS complet
│   ├── risk_scoring.py        # Calcul scores risque
│   ├── export_service.py      # Export PDF/JSON
│   └── redis_session.py       # Gestion sessions Redis
│
├── ml/                         # Machine Learning
│   ├── __init__.py
│   ├── train_model.py         # Entraînement RandomForest
│   ├── predict.py             # Prédictions temps réel
│   └── model.pkl              # généré par train_model.py (non versionné, >100 Mo)
│
├── templates/                  # Templates HTML
│   ├── base.html              # Template de base
│   ├── login.html             # Page login
│   ├── dashboard.html         # Dashboard SOC
│   ├── logs.html              # Gestion logs
│   ├── alerts.html            # Gestion alerts
│   ├── users.html             # Gestion users
│   ├── sessions.html          # Sessions user
│   └── admin_sessions.html    # Sessions admin
│
├── static/                     # Fichiers statiques
│   ├── css/
│   │   └── style.css          # CSS personnalisé
│   └── js/
│       └── dashboard.js       # Chart.js + interactions
│
├── data/                       # Données
│   ├── demo_data.py           # Script génération démo
│   ├── test_logs.csv          # CSV test (500+ lignes)
│   └── test_alerts.json       # JSON test alerts
│
├── database/                   # Scripts init bases
│   ├── init_users.sql         # Init table SQL users
│   ├── init_logs.js           # Init collections MongoDB
│   └── init_sessions.sh       # Init sessions Redis test
│
└── uploads/                    # CSV temporaires (créé auto)
```

---

## API

### Authentification

**POST** `/login`
```bash
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123"
```

**GET** `/logout`

### Logs

**GET** `/api/logs?limit=100`
```bash
curl http://localhost:5000/api/logs?limit=10
```

**POST** `/api/logs/ingest`
```bash
curl -X POST http://localhost:5000/api/logs/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.1",
    "destination_ip": "10.0.0.1",
    "destination_port": 80,
    "flow_duration": 5000,
    "flow_bytes_per_second": 15000,
    "flow_packets_per_second": 150
  }'
```

### Alerts

**GET** `/api/alerts?limit=100`

### Prédictions ML

**POST** `/api/predict`
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "destination_port": 80,
    "flow_duration": 5000,
    "flow_bytes_per_second": 150000,
    "flow_packets_per_second": 1500
  }'
```

**Réponse** :
```json
{
  "label": "DDoS",
  "confidence": 0.95,
  "probabilities": {
    "DDoS": 0.95,
    "BENIGN": 0.03,
    "PortScan": 0.02
  }
}
```

---

## Tests


**1. Test connexion bases** :
```bash
# SQL
python -c "from config.config import db; print('SQL OK')"

# MongoDB
python -c "from config.config import get_mongo_db; db=get_mongo_db(); print('MongoDB OK')"

# Redis
python -c "from config.config import redis_client; redis_client.ping(); print('Redis OK')"
```

**2. Test ML** :
```bash
python ml/predict.py
```

---

## Dépannage

### MongoDB ne démarre pas

**Windows** :
```powershell
# Vérifier service
Get-Service MongoDB

# Redémarrer
net stop MongoDB
net start MongoDB
```

### Redis non disponible

**Erreur** : `ERREUR: Redis non disponible`

**Solution** :
```bash
# Vérifier
redis-cli ping

# Ou installer localement
sudo apt-get install redis-server
```

### Modèle ML introuvable

**Erreur** : `FileNotFoundError: Model not found`

**Solution** :
```bash
# Vérifier dataset existe
ls C:\Users\oussa\Desktop\MachineLearningCSV\final_dataset.csv

# Réentraîner modèle
python ml/train_model.py
```

### Import CSV échoue

**Erreur** : `Colonnes manquantes`

**Solution** :
Vérifier CSV contient colonnes obligatoires :
- `destination_port`
- `flow_duration`
- `flow_bytes_per_second`
- `flow_packets_per_second`

Exemple format correct dans `data/test_logs.csv`

---

## Auteur

**LAGRINI Mohamed Abdellah**
---

**SentinelAI - Protégez votre réseau avec l'intelligence artificielle**