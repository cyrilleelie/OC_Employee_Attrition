import pandas as pd
# Supprimé: from sqlalchemy import create_engine # Nous utiliserons la session/engine de database_setup
from src.database.database_setup import SessionLocal, engine # Importer SessionLocal et engine
from src.database.models import Employee # Importer votre modèle Employee
from src import config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data_from_csv(path=config.PROCESSED_DATA_PATH):
    """Charge les données depuis un fichier CSV (gardé pour référence ou fallback)."""
    try:
        logger.info(f"Chargement des données CSV depuis {path}...")
        df = pd.read_csv(path)
        logger.info("Données CSV chargées avec succès.")
        return df
    except FileNotFoundError:
        logger.error(f"Fichier CSV non trouvé : {path}")
        return None

def load_data_from_postgres() -> pd.DataFrame:
    """Charge les données de la table 'employees' depuis PostgreSQL dans un DataFrame."""
    db = SessionLocal()
    try:
        logger.info("Chargement des données depuis la table 'employees' de PostgreSQL...")
        # Construire la requête pour sélectionner toutes les colonnes de la table Employee
        query = db.query(Employee)
        # Exécuter la requête et la charger dans un DataFrame Pandas
        df = pd.read_sql_query(query.statement, db.bind) # Utiliser db.bind pour la connexion
        
        if df.empty:
            logger.warning("Aucune donnée trouvée dans la table 'employees'. Le DataFrame est vide.")
        else:
            logger.info(f"{len(df)} lignes chargées depuis la table 'employees'.")
        return df
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données depuis PostgreSQL : {e}", exc_info=True)
        return pd.DataFrame() # Retourner un DataFrame vide en cas d'erreur
    finally:
        db.close()

def get_data(source: str = "postgres") -> pd.DataFrame: # Changement de la source par défaut
    """
    Fonction principale pour charger les données.
    'source' peut être "postgres" ou "csv".
    """
    logger.info(f"Récupération des données depuis la source : {source}")
    if source == "postgres":
        return load_data_from_postgres()
    elif source == "csv":
        # Vous pourriez vouloir charger le CSV fusionné et nettoyé si vous l'aviez sauvegardé,
        # ou relancer le processus de fusion si vous voulez repartir des bruts.
        # Pour l'instant, on garde la logique précédente si 'csv' est appelé.
        # Si vous avez un fichier CSV qui correspond à ce qui est dans la BDD:
        # return load_data_from_csv(config.PROCESSED_DATA_PATH)
        # Sinon, si vous voulez repartir des bruts (ce qui est moins pertinent maintenant):
        from .load_data import load_and_merge_csvs # Assurez-vous que cette fonction existe toujours
        logger.warning("Chargement depuis les CSV bruts via load_and_merge_csvs. Cette source est moins recommandée maintenant.")
        return load_and_merge_csvs() # Si load_and_merge_csvs est toujours là et fait le travail
    else:
        logger.error(f"Source de données non reconnue : {source}. Utilisation de PostgreSQL par défaut.")
        return load_data_from_postgres()


# La fonction load_and_merge_csvs() peut être gardée si vous en avez encore besoin pour
# peupler la base ou pour d'autres usages, sinon elle pourrait être enlevée à terme.
# Assurez-vous qu'elle est toujours présente si get_data(source="csv") l'appelle.
# Pour l'instant, nous la laissons pour ne pas casser le script de peuplement si vous l'avez utilisé.
def load_and_merge_csvs():
    """Charge les 3 fichiers CSV bruts, prépare la clé de jointure et les fusionne."""
    try:
        logger.info("Chargement des fichiers CSV bruts...")
        df_sirh = pd.read_csv(config.RAW_SIRH_PATH)
        df_eval = pd.read_csv(config.RAW_EVAL_PATH)
        df_sondage = pd.read_csv(config.RAW_SONDAGE_PATH)

        logger.info("Préparation de la clé de jointure dans df_eval...")
        if 'eval_number' in df_eval.columns:
            df_eval['id_employee_str'] = df_eval['eval_number'].str.split('_').str[1]
            df_eval['id_employee'] = pd.to_numeric(df_eval['id_employee_str'], errors='coerce')
            nan_count = df_eval['id_employee'].isnull().sum()
            if nan_count > 0:
                logger.warning(f"{nan_count} 'eval_number' n'ont pas pu être convertis en 'id_employee' valides.")
            df_eval['id_employee'] = df_eval['id_employee'].astype('object') # Garder en object pour correspondre à String(255)
            df_eval = df_eval.drop(columns=['id_employee_str'])
        else:
            logger.error("La colonne 'eval_number' est introuvable dans df_eval.")
            return None

        for df_temp, name in [(df_sirh, 'df_sirh'), (df_sondage, 'df_sondage')]:
            if 'id_employee' in df_temp.columns:
                 df_temp['id_employee'] = df_temp['id_employee'].astype('object')
            else:
                logger.error(f"La colonne 'id_employee' est introuvable dans {name}.")
                return None

        logger.info("Fusion des DataFrames...")
        df_merged = pd.merge(df_sirh, df_eval, on='id_employee', how='left')
        df_merged = pd.merge(df_merged, df_sondage, on='id_employee', how='left')

        logger.info(f"Données fusionnées : {df_merged.shape}")
        return df_merged

    except FileNotFoundError as e:
        logger.error(f"Erreur de chargement CSV : Fichier non trouvé - {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement/fusion CSV : {e}", exc_info=True)
        return None


# Pour tester ce module : poetry run python -m src.data_processing.load_data
if __name__ == "__main__":
    logger.info("--- Test du chargement depuis PostgreSQL ---")
    data_from_db = get_data(source="postgres")
    if data_from_db is not None and not data_from_db.empty:
        print(data_from_db.head())
        print(f"\nDimensions des données depuis DB : {data_from_db.shape}")
        print(f"\nTypes de données depuis DB :\n{data_from_db.dtypes}")
    else:
        print("Aucune donnée chargée depuis la base ou une erreur s'est produite.")

    # logger.info("\n--- Test du chargement depuis CSV (si toujours pertinent) ---")
    # data_from_csv = get_data(source="csv") # Nécessiterait les CSV bruts
    # if data_from_csv is not None:
    #     print(data_from_csv.head())