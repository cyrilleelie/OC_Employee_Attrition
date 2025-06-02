"""
Script pour peupler la table 'employees' dans la base de données PostgreSQL
à partir des fichiers CSV bruts.

Ce script effectue les opérations suivantes :
1. Charge et fusionne les données des fichiers CSV source.
2. Applique les transformations initiales de nettoyage et de feature engineering.
3. Itère sur le DataFrame résultant et insère chaque ligne dans la table 'employees'
   en utilisant SQLAlchemy.
"""

import pandas as pd
import logging
from sqlalchemy.orm import Session

from src.database.database_setup import SessionLocal
from src.database.models import Employee
from src.data_processing.load_data import load_and_merge_csvs
from src.data_processing.preprocess import (
    clean_data,
    map_binary_features,
    create_features,
)
from src import config  # Pour config.BINARY_FEATURES_MAPPING

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def populate_db():
    """
    Charge les données depuis les fichiers CSV, les transforme, et les insère
    dans la table 'employees' de la base de données.

    S'assure que les données sont préparées (nettoyées, features binaires mappées,
    features créées) avant l'insertion. Gère la session de base de données
    pour les opérations d'écriture.
    """
    logger.info("Début du peuplement de la table 'employees'...")

    logger.info("Chargement et fusion des données CSV brutes...")
    df_raw = load_and_merge_csvs()
    if df_raw is None:
        logger.error("Impossible de charger les données CSV. Arrêt du peuplement.")
        return

    logger.info("Application des transformations initiales des données...")
    # clean_data devrait maintenant conserver 'id_employee' si c'est votre clé
    df_cleaned = clean_data(df_raw)
    df_mapped = map_binary_features(df_cleaned, config.BINARY_FEATURES_MAPPING)
    df_processed_for_db = create_features(df_mapped)

    if df_processed_for_db.empty:
        logger.warning(
            "Le DataFrame est vide après les transformations. Aucune donnée à insérer."
        )
        return

    logger.info(
        f"Données prêtes à être insérées : {df_processed_for_db.shape[0]} lignes."
    )

    db: Session = SessionLocal()
    insert_count = 0
    skipped_count = 0
    try:
        logger.info("Début de l'insertion des données dans la table 'employees'...")
        for index, row_data in df_processed_for_db.iterrows():
            employee_data_dict = row_data.to_dict()

            pk_name = (
                "id_employee"  # Nom de l'attribut clé primaire dans le modèle Employee
            )

            # Vérifier la présence et la validité de la clé primaire
            if pk_name not in employee_data_dict or pd.isna(
                employee_data_dict.get(pk_name)
            ):
                logger.warning(
                    f"Clé primaire '{pk_name}' (valeur: {employee_data_dict.get(pk_name)}) "
                    f"manquante ou NaN pour la ligne avec index de DataFrame {index}. Ligne ignorée."
                )
                skipped_count += 1
                continue

            # Filtrer les données pour ne garder que les colonnes du modèle Employee
            # et convertir les NaN de Pandas en None pour SQLAlchemy
            model_columns = {c.name for c in Employee.__table__.columns}
            filtered_data_for_model = {
                k: (None if pd.isna(v) else v)
                for k, v in employee_data_dict.items()
                if k in model_columns
            }

            # Assurer que la clé primaire a toujours une valeur après filtrage
            if filtered_data_for_model.get(pk_name) is None:
                logger.warning(
                    f"Clé primaire '{pk_name}' devenue None après filtrage pour la ligne "
                    f"avec index de DataFrame {index}. Ligne ignorée."
                )
                skipped_count += 1
                continue

            # Optionnel : Vérifier si l'employé existe déjà pour éviter les doublons
            # existing_employee = db.query(Employee).filter(Employee.id_employee == filtered_data_for_model[pk_name]).first()
            # if existing_employee:
            #     logger.info(f"L'employé {filtered_data_for_model[pk_name]} existe déjà. Ignoré.")
            #     skipped_count +=1
            #     continue

            employee_to_insert = Employee(**filtered_data_for_model)
            db.add(employee_to_insert)
            insert_count += 1

        db.commit()
        logger.info(
            f"{insert_count} lignes insérées avec succès dans la table 'employees'."
        )
        if skipped_count > 0:
            logger.info(
                f"{skipped_count} lignes ont été ignorées (ID manquant/NaN ou déjà existant)."
            )

    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'insertion des données : {e}", exc_info=True)
        # 'raise e' pourrait être remplacé par juste 'raise' pour relancer l'exception attrapée
        # ou ne pas la relancer si vous voulez que le script se termine "proprement" après une erreur.
        # Pour un script de peuplement, il est souvent bon de savoir s'il y a eu une erreur majeure.
        raise
    finally:
        db.close()
        logger.info("Session de base de données fermée.")


if __name__ == "__main__":
    logger.info("--- Démarrage du script de peuplement de la base de données ---")
    # IMPORTANT : Ce script est conçu pour un premier peuplement.
    # Si vous le relancez sur une base déjà peuplée, il tentera de réinsérer les données,
    # ce qui causera des erreurs si les 'id_employee' sont uniques (clé primaire).
    # Pour des exécutions multiples, implémentez une logique de suppression préalable
    # ou de vérification d'existence (comme le bloc commenté ci-dessus).

    # Exemple de suppression préalable (à utiliser avec prudence !) :
    # logger.info("Tentative de suppression des données existantes de la table 'employees'...")
    # temp_db = SessionLocal()
    # try:
    #     num_rows_deleted = temp_db.query(Employee).delete()
    #     temp_db.commit()
    #     logger.info(f"{num_rows_deleted} lignes supprimées de la table 'employees'.")
    # except Exception as e_del:
    #     temp_db.rollback()
    #     logger.error(f"Erreur lors de la suppression des données existantes : {e_del}")
    # finally:
    #     temp_db.close()

    populate_db()
    logger.info("--- Script de peuplement de la base de données terminé ---")
