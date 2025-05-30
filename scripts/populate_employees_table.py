# Dans scripts/populate_employees_table.py
import pandas as pd
import logging
from sqlalchemy.orm import Session

from src.database.database_setup import SessionLocal, engine # Pour créer une session BDD
from src.database.models import Employee # Votre modèle SQLAlchemy pour la table Employee
# Importez les fonctions de chargement et de nettoyage que vous utilisiez pour les CSV
from src.data_processing.load_data import load_and_merge_csvs
from src.data_processing.preprocess import clean_data, map_binary_features, create_features
from src import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_db():
    logger.info("Chargement et préparation des données depuis les CSV...")
    df_raw = load_and_merge_csvs()
    if df_raw is None:
        logger.error("Impossible de charger les données CSV. Arrêt du peuplement.")
        return

    # Récupérer le mapping depuis config.py
    current_binary_mapping = config.BINARY_FEATURES_MAPPING

    # Appliquer les transformations initiales pour avoir les données
    # dans le format attendu par la table 'employees'
    df_cleaned = clean_data(df_raw) # Fait la conversion cible, supprime cols, convertit "XX %"
    df_mapped = map_binary_features(df_cleaned, current_binary_mapping) # Mappe genre, heure_sup
    df_featured = create_features(df_mapped) # Si vous avez des features créées ici
                                              # qui doivent être stockées

    # La cible est déjà dans df_featured sous config.TARGET_VARIABLE
    # Assurez-vous que les noms de colonnes de df_featured correspondent à ceux de votre modèle Employee
    # et que les types sont compatibles.

    logger.info(f"Données prêtes à être insérées : {df_featured.shape[0]} lignes.")

    db: Session = SessionLocal()
    try:
        logger.info("Insertion des données dans la table 'employees'...")
        insert_count = 0
        for index, row in df_featured.iterrows():
            # Créez un dictionnaire des données de la ligne
            # en s'assurant que les clés correspondent aux attributs du modèle Employee
            employee_data = row.to_dict()

            # Si votre modèle Employee a des noms d'attributs différents des colonnes du DataFrame
            # vous devrez faire un mappage explicite ici.
            # Par exemple, si df_featured a 'id_employee' et votre modèle a 'employee_id':
            # employee_obj_data = {'employee_id': employee_data.get('id_employee'), ...}

            # Pour cet exemple, on suppose que les noms de colonnes du DataFrame final
            # (après clean, map, feature) correspondent aux attributs du modèle Employee.
            # Assurez-vous que employee_id est bien dans employee_data
            if 'id_employee' not in employee_data and hasattr(Employee, 'id_employee'):
                 # Essayez de récupérer l'id depuis l'index si c'était la clé
                 employee_data['id_employee'] = index if isinstance(index, str) else str(index)


            # Gérer le cas où la clé primaire 'id_employee' pourrait ne pas être dans row.to_dict()
            # si elle faisait partie de l'index et n'est pas une colonne régulière.
            # Ou si le nom de la colonne dans le DF est différent de l'attribut du modèle.
            # Adaptez cette partie à votre structure exacte.

            # Création de l'objet Employee
            # On ne passe que les clés qui existent dans le modèle Employee pour éviter les erreurs
            model_columns = {c.name for c in Employee.__table__.columns}
            filtered_employee_data = {k: v for k, v in employee_data.items() if k in model_columns}


            # Spécifiquement pour la clé primaire si elle vient de l'index
            if 'id_employee' not in filtered_employee_data and hasattr(Employee, 'id_employee'):
                if isinstance(index, tuple) and len(index) > 0: # MultiIndex
                     # Décidez quelle partie de l'index utiliser ou comment la formater
                    filtered_employee_data['id_employee'] = str(index[0]) # Exemple
                else:
                    filtered_employee_data['id_employee'] = str(index)


            # Assurez-vous que la clé primaire a une valeur
            pk_name = 'id_employee' # ou le nom de votre PK dans le modèle Employee
            if pk_name not in filtered_employee_data or pd.isna(filtered_employee_data.get(pk_name)):
                logger.warning(f"Clé primaire '{pk_name}' manquante ou NaN pour la ligne d'index {index}. Ligne ignorée.")
                continue


            # Vérifier si l'employé existe déjà pour éviter les doublons (facultatif, dépend de votre logique)
            # existing_employee = db.query(Employee).filter(Employee.id_employee == filtered_employee_data[pk_name]).first()
            # if existing_employee:
            #     logger.info(f"L'employé {filtered_employee_data[pk_name]} existe déjà. Mise à jour ou ignoré.")
            #     # Vous pouvez choisir de mettre à jour ou d'ignorer
            #     continue


            employee_to_insert = Employee(**filtered_employee_data)
            db.add(employee_to_insert)
            insert_count += 1

        db.commit()
        logger.info(f"{insert_count} lignes insérées/mises à jour dans 'employees'.")
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'insertion des données : {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # IMPORTANT : Avant de lancer ce script, assurez-vous que la table 'employees'
    # est vide si vous voulez éviter les doublons ou gérez les conflits.
    # Pour une première exécution, c'est ok. Pour des exécutions répétées,
    # il faudrait une logique pour éviter d'insérer les mêmes données.
    # Par exemple, supprimer toutes les données de la table avant :
    # from src.database.models import Employee
    # db = SessionLocal()
    # try:
    #     num_rows_deleted = db.query(Employee).delete()
    #     db.commit()
    #     logger.info(f"{num_rows_deleted} lignes supprimées de la table employees.")
    # except:
    #     db.rollback()
    # finally:
    #     db.close()
    populate_db()