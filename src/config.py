import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement (pour les secrets)
load_dotenv()

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
# NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Fichiers de données (Adaptez les noms !)
RAW_SIRH_PATH = DATA_DIR / "raw" / "extrait_sirh.csv"
RAW_EVAL_PATH = DATA_DIR / "raw" / "extrait_eval.csv"
RAW_SONDAGE_PATH = DATA_DIR / "raw" / "extrait_sondage.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "data_rh_final.csv" # Le fichier après fusion/nettoyage initial

# Modèle (Adaptez le nom !)
MODEL_NAME = "attrition_logistic_regression.joblib"
MODEL_PATH = MODELS_DIR / MODEL_NAME

# Variable Cible
TARGET_VARIABLE = 'a_quitte_l_entreprise_numeric' # Utilisez la version numérique

# Colonnes (Exemples - Adaptez !)
# Vous pourriez lister ici les colonnes numériques/catégorielles
# si elles sont fixes, ou les déterminer dynamiquement.

# Configuration Base de Données
DB_USER = os.getenv("POSTGRES_USER", "default_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "attrition_db")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuration API
API_TITLE = "API de Prédiction d'Attrition RH"
API_VERSION = "0.1.0"

# Créez le dossier models s'il n'existe pas
MODELS_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)