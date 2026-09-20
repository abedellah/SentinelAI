# init.ps1 - Script d'initialisation SentinelAI pour Windows
# Encodage UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SentinelAI - Initialisation du projet" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérification Python
Write-Host "[1/7] Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERREUR: Python non trouvé. Installez Python 3.12" -ForegroundColor Red
    exit 1
}

# Création environnement virtuel
Write-Host "`n[2/7] Création de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  venv existe déjà, utilisation de l'existant" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "  venv créé avec succès" -ForegroundColor Green
}

# Activation venv
Write-Host "`n[3/7] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  venv activé" -ForegroundColor Green

# Installation des dépendances
Write-Host "`n[4/7] Installation des dépendances Python..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "  Dépendances installées" -ForegroundColor Green

# Vérification MongoDB
Write-Host "`n[5/7] Vérification du service MongoDB..." -ForegroundColor Yellow
$mongoService = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
if ($mongoService) {
    if ($mongoService.Status -eq "Running") {
        Write-Host "  MongoDB est déjà en cours d'exécution" -ForegroundColor Green
    } else {
        Write-Host "  Démarrage de MongoDB..." -ForegroundColor Yellow
        Start-Service MongoDB
        Write-Host "  MongoDB démarré" -ForegroundColor Green
    }
} else {
    Write-Host "  ATTENTION: Service MongoDB non trouvé" -ForegroundColor Red
    Write-Host "  Installez MongoDB Community Edition pour Windows" -ForegroundColor Red
    Write-Host "  URL: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
}

# Génération des données de démo
Write-Host "`n[6/7] Génération des données de démonstration..." -ForegroundColor Yellow
python data\demo_data.py
Write-Host "  Données de démo générées" -ForegroundColor Green

# Vérification du dataset ML
Write-Host "`n[7/7] Vérification du dataset ML..." -ForegroundColor Yellow
$datasetPath = "C:\Users\oussa\Desktop\MachineLearningCSV\final_dataset.csv"
if (Test-Path $datasetPath) {
    Write-Host "  Dataset trouvé: $datasetPath" -ForegroundColor Green
    Write-Host "`n  Entraînement du modèle ML..." -ForegroundColor Yellow
    python ml\train_model.py
    Write-Host "  Modèle entraîné et sauvegardé" -ForegroundColor Green
} else {
    Write-Host "  ATTENTION: Dataset non trouvé: $datasetPath" -ForegroundColor Red
    Write-Host "  Le modèle ML ne sera pas disponible sans dataset" -ForegroundColor Yellow
}

# Fin
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  INITIALISATION TERMINÉE AVEC SUCCÈS" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour lancer SentinelAI:" -ForegroundColor Yellow
Write-Host "  1. Assurez-vous que MongoDB est lancé" -ForegroundColor White
Write-Host "  2. Exécutez: python app.py" -ForegroundColor White
Write-Host "  3. Accédez à: http://localhost:5000" -ForegroundColor White
Write-Host "  4. Connectez-vous avec: admin / admin123" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "  Activer venv    : .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  Lancer app      : python app.py" -ForegroundColor White
Write-Host "  Réinitialiser DB: python data\demo_data.py" -ForegroundColor White
Write-Host "  Réentraîner ML  : python ml\train_model.py" -ForegroundColor White
Write-Host ""