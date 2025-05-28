import pandas as pd
from sqlalchemy import create_engine
from src import config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_merge_csvs():
    """Charge les 3 fichiers CSV bruts et les fusionne."""
    try:
        logger.info("Chargement des fichiers CSV bruts...")
        df_sirh = pd.read_csv(config.RAW_SIRH_PATH)
        df_eval = pd.read_csv(config.RAW_EVAL_PATH)
        df_sondage = pd.read_csv(config.RAW_SONDAGE_PATH)

        # Création de la donnée id_employee dans le dataframe df_eval pour faire la jointure avec cette donné dans le dataframe df_sirh
        df_eval['id_employee'] = df_eval['eval_number'].str[2:].astype('int64')

        logger.info("Fusion des DataFrames...")
        df_merged = df_sirh.merge(df_eval, left_on='id_employee', right_on='id_employee', suffixes=('_sirh', '_eval'), how='left').copy()
        df_merged = df_merged.merge(df_sondage, left_on='id_employee', right_on='code_sondage', suffixes=('_sirh', '_sondage'), how='left').copy()

        logger.info(f"Données fusionnées : {df_merged.shape}")
        return df_merged

    except FileNotFoundError as e:
        logger.error(f"Erreur de chargement CSV : Fichier non trouvé - {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement/fusion CSV : {e}")
        return None

def load_processed_data(path=config.PROCESSED_DATA_PATH):
    """Charge les données déjà traitées (si elles existent)."""
    try:
        logger.info(f"Chargement des données traitées depuis {path}...")
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        logger.warning(f"Fichier de données traitées non trouvé : {path}. Il faudra le générer.")
        return None

def load_from_postgres(table_name="employees_attrition_data"):
    """Charge les données depuis PostgreSQL (pour l'avenir)."""
    logger.warning("Fonctionnalité PostgreSQL non implémentée.")
    # (Code de la réponse précédente pour PostgreSQL ici)
    return None

# Pour tester ce module : python src/data_processing/load_data.py
if __name__ == "__main__":
    df = load_and_merge_csvs()
    if df is not None:
        print("Chargement et fusion réussis :")
        print(df.head())