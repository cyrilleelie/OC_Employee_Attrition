# Dans src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

RAW_SIRH_PATH = DATA_DIR / "raw" / "extrait_sirh.csv"
RAW_EVAL_PATH = DATA_DIR / "raw" / "extrait_eval.csv"
RAW_SONDAGE_PATH = DATA_DIR / "raw" / "extrait_sondage.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "data_rh_final.csv"

MODEL_NAME = "attrition_logistic_regression.joblib"
MODEL_PATH = MODELS_DIR / MODEL_NAME

TARGET_VARIABLE = "a_quitte_l_entreprise_numeric"

DB_USER = os.getenv("POSTGRES_USER", "default_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "attrition_db")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

API_TITLE = "API de Prédiction d'Attrition RH"
API_VERSION = "0.1.0"

ENABLE_API_DB_LOGGING = os.getenv("ENABLE_API_DB_LOGGING", "false").lower() == "true"

BINARY_FEATURES_MAPPING = {
    "genre": {"M": 0, "F": 1},
    "heure_supplementaires": {"Non": 0, "Oui": 1}
}

ORDINAL_FEATURES_CATEGORIES = {
    "frequence_deplacement": ["Aucun", "Occasionnel", "Frequent"]
}

LIMITED_VALUES_FEATURES = {
    "statut_marital": ["Célibataire", "Marié(e)", "Divorcé(e)"],
    "departement": ["Commercial", "Consulting", "Ressources Humaines"],
    "poste": ["Cadre Commercial", "Assistant de Direction", "Consultant", "Tech Lead", "Manager", "Représentant Commercial", "Directeur Technique", "Senior Manager", "Ressources Humaines"],
    "domaine_etude": ["Infra & Cloud", "Autre", "Transformation Digitale", "Marketing", "Entrepreunariat", "Ressources Humaines"]
}