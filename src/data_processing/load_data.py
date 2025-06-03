"""
Module pour le chargement et la préparation initiale des données.

Fonctions pour charger les données brutes depuis des fichiers CSV, les fusionner, et préparer les clés de jointure. Fournit également des fonctions pour charger les données depuis une base de données PostgreSQL une fois peuplée.
La fonction principale `get_data` sert d'interface pour obtenir les données pour le reste de l'application, typiquement pour l'entraînement du modèle.

"""

import pandas as pd
from sqlalchemy.orm import (
    Session,
)  # Importé pour être utilisé dans load_data_from_postgres

from src.database.database_setup import (
    SessionLocal,
)  # engine est utilisé implicitement par read_sql_query via db.bind
from src.database.models import Employee
from src import config
import logging

# Configuration du logging pour ce module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_data_from_csv(path: str = config.PROCESSED_DATA_PATH) -> pd.DataFrame | None:
    """
    Charge les données depuis un unique fichier CSV spécifié.

    Utilisé comme fonction de secours ou pour charger un dataset déjà traité et sauvegardé en CSV.

    Args:
        path (str, optional): Chemin vers le fichier CSV.
                              Par défaut, utilise config.PROCESSED_DATA_PATH.

    Returns:
        pd.DataFrame | None: DataFrame Pandas contenant les données chargées,
                             ou None si le fichier n'est pas trouvé.
    """
    try:
        logger.info(f"Chargement des données CSV depuis {path}...")
        df = pd.read_csv(path)
        logger.info(
            f"Données CSV chargées avec succès depuis {path}: {df.shape[0]} lignes."
        )
        return df
    except FileNotFoundError:
        logger.error(f"Fichier CSV non trouvé : {path}")
        return None
    except Exception as e:
        logger.error(
            f"Erreur inattendue lors du chargement du CSV {path}: {e}", exc_info=True
        )
        return None


def load_data_from_postgres() -> pd.DataFrame:
    """
    Charge l'intégralité des données de la table 'employees' depuis PostgreSQL
    dans un DataFrame Pandas.

    Utilise SQLAlchemy pour interagir avec la base de données configurée.

    Returns:
        pd.DataFrame: DataFrame Pandas contenant les données de la table 'employees'.
                      Retourne un DataFrame vide en cas d'erreur ou si la table est vide.
    """
    db: Session = SessionLocal()
    try:
        logger.info(
            "Chargement des données depuis la table 'employees' de PostgreSQL..."
        )
        query = db.query(
            Employee
        )  # Construit une requête pour sélectionner toutes les colonnes de Employee
        # Exécute la requête et charge les résultats dans un DataFrame Pandas
        df = pd.read_sql_query(sql=query.statement, con=db.bind)

        if df.empty:
            logger.warning(
                "Aucune donnée trouvée dans la table 'employees'. Le DataFrame est vide."
            )
        else:
            logger.info(f"{len(df)} lignes chargées depuis la table 'employees'.")
        return df
    except Exception as e:
        logger.error(
            f"Erreur lors du chargement des données depuis PostgreSQL : {e}",
            exc_info=True,
        )
        return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur
    finally:
        db.close()
        logger.debug("Session PostgreSQL fermée pour load_data_from_postgres.")


def get_data(source: str = "postgres") -> pd.DataFrame | None:
    """
    Fonction principale pour obtenir le jeu de données pour l'application.

    Sert d'interface pour charger les données soit depuis PostgreSQL (par défaut),
    soit depuis des fichiers CSV bruts (via `load_and_merge_csvs`).

    Args:
        source (str, optional): La source des données. Peut être "postgres" ou "csv".
                                Par défaut à "postgres".

    Returns:
        pd.DataFrame | None: DataFrame Pandas contenant les données, ou None si une
                             erreur majeure de chargement se produit (ex: CSV introuvables).
                             Peut retourner un DataFrame vide si la source est vide (ex: table PG vide).
    """
    logger.info(f"Récupération des données depuis la source : {source}")
    if source == "postgres":
        return load_data_from_postgres()
    elif source == "csv":
        logger.warning(
            "Chargement depuis les CSV bruts via load_and_merge_csvs. "
            "Cette source est principalement pour le peuplement initial de la BDD."
        )
        # L'import local est inhabituel. S'il est utilisé, il devrait être en haut du fichier.
        # Cependant, si load_and_merge_csvs est spécifique à ce cas, le garder ici
        # évite un import circulaire si load_and_merge_csvs devait importer qqch de ce module.
        # Pour l'instant, nous le laissons, mais c'est un point d'attention.
        # from .load_data import load_and_merge_csvs # Ceci créerait une récursion.
        # Il faut s'assurer que load_and_merge_csvs est bien défini dans ce même fichier.
        return load_and_merge_csvs()
    else:
        logger.error(
            f"Source de données non reconnue : {source}. Tentative avec PostgreSQL par défaut."
        )
        return load_data_from_postgres()


def load_and_merge_csvs() -> pd.DataFrame | None:
    """
    Charge les données depuis les trois fichiers CSV bruts (`extrait_sirh.csv`,
    `extrait_eval.csv`, `extrait_sondage.csv`), prépare les clés de jointure `id_employee`
    (notamment à partir de `eval_number` et `code_sondage`), et fusionne les DataFrames.

    Cette fonction est principalement utilisée pour le peuplement initial de la base de données.
    Elle s'assure que les `id_employee` sont traités comme des chaînes de caractères pour
    des fusions cohérentes.

    Returns:
        pd.DataFrame | None: Un DataFrame fusionné contenant les données des trois sources,
                             ou None si une erreur critique se produit (ex: fichier introuvable,
                             colonne clé de jointure manquante).
    """
    try:
        logger.info("Chargement des fichiers CSV bruts pour fusion...")
        df_sirh = pd.read_csv(config.RAW_SIRH_PATH)
        df_eval = pd.read_csv(config.RAW_EVAL_PATH)
        df_sondage = pd.read_csv(config.RAW_SONDAGE_PATH)

        # Préparation de df_eval
        logger.info(
            "Préparation de la clé de jointure 'id_employee' dans df_eval à partir de 'eval_number'..."
        )
        if "eval_number" in df_eval.columns:
            df_eval["id_employee_str_temp"] = (
                df_eval["eval_number"]
                .astype(str)
                .str.split("_", n=1)
                .str.get(1)  # Prend tout après le premier '_'
            )
            numeric_ids_for_check = pd.to_numeric(
                df_eval["id_employee_str_temp"], errors="coerce"
            )
            nan_count = numeric_ids_for_check.isnull().sum()
            if nan_count > 0:
                logger.warning(
                    f"{nan_count} 'eval_number' (après extraction) n'ont pas pu être convertis "
                    f"en id_employee numériques valides et sont devenus NaN."
                )
            df_eval["id_employee"] = df_eval["id_employee_str_temp"].astype(
                str
            )  # Clé finale en string
            df_eval = df_eval.drop(columns=["id_employee_str_temp"])
            logger.info("'id_employee' créé et formaté en string dans df_eval.")
        else:
            logger.error(
                "La colonne 'eval_number' est introuvable dans df_eval. Impossible de créer 'id_employee'."
            )
            return None

        # Préparation de df_sondage
        logger.info(
            "Préparation de la clé de jointure 'id_employee' dans df_sondage à partir de 'code_sondage'..."
        )
        if (
            "code_sondage" in df_sondage.columns
        ):  # Supposons que code_sondage est directement l'id_employee
            # Si code_sondage nécessite une transformation similaire à eval_number, appliquez-la ici.
            # Pour cet exemple, on suppose que code_sondage EST l'id_employee.
            df_sondage["id_employee"] = df_sondage["code_sondage"].astype(str)
            # Si vous aviez 'id_employee_str_temp' ici aussi, n'oubliez pas de le drop.
            logger.info(
                "'id_employee' (depuis code_sondage) formaté en string dans df_sondage."
            )
        else:
            # Si 'code_sondage' n'existe pas, on pourrait vérifier si 'id_employee' existe déjà
            if "id_employee" not in df_sondage.columns:
                logger.error(
                    "Ni 'code_sondage' ni 'id_employee' trouvés dans df_sondage."
                )
                return None
            else:  # id_employee existe déjà, on s'assure juste du type
                df_sondage["id_employee"] = df_sondage["id_employee"].astype(str)
                logger.info("'id_employee' existant dans df_sondage formaté en string.")

        # Standardisation du type de 'id_employee' dans df_sirh
        if "id_employee" in df_sirh.columns:
            df_sirh["id_employee"] = df_sirh["id_employee"].astype(str)
        else:
            logger.error("La colonne 'id_employee' est introuvable dans df_sirh.")
            return None

        logger.info("Fusion des DataFrames (df_sirh <- df_eval <- df_sondage)...")
        df_merged = pd.merge(df_sirh, df_eval, on="id_employee", how="left")
        df_merged = pd.merge(df_merged, df_sondage, on="id_employee", how="left")

        logger.info(
            f"Données fusionnées avec succès : {df_merged.shape[0]} lignes, {df_merged.shape[1]} colonnes."
        )
        return df_merged

    except FileNotFoundError as e:
        logger.error(f"Erreur de chargement CSV : Fichier non trouvé - {e}")
        return None
    except Exception as e:
        logger.error(
            f"Erreur inattendue lors du chargement/fusion CSV : {e}", exc_info=True
        )
        return None


if __name__ == "__main__":
    logger.info("--- Test du chargement des données depuis PostgreSQL ---")
    data_from_db = get_data(source="postgres")
    if data_from_db is not None and not data_from_db.empty:
        print("Premières lignes de data_from_db:")
        print(data_from_db.head())
        print(f"\nDimensions des données depuis DB : {data_from_db.shape}")
        # print(f"\nTypes de données depuis DB :\n{data_from_db.dtypes}") # Peut être verbeux
    else:
        print(
            "Aucune donnée chargée depuis la base ou une erreur s'est produite lors du chargement."
        )

    # Décommentez pour tester le chargement et la fusion des CSV bruts
    # logger.info("\n--- Test du chargement et de la fusion des CSV bruts ---")
    # data_from_csv_merge = get_data(source="csv")
    # if data_from_csv_merge is not None and not data_from_csv_merge.empty:
    #     print("\nPremières lignes de data_from_csv_merge:")
    #     print(data_from_csv_merge.head())
    #     print(f"\nDimensions des données fusionnées depuis CSV : {data_from_csv_merge.shape}")
    # else:
    #     print("Aucune donnée chargée depuis les CSV ou une erreur s'est produite lors de la fusion.")
