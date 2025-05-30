import pandas as pd
from joblib import load
import logging
from src import config
from typing import List, Dict, Union

# Importer les fonctions de preprocessing nécessaires !
from src.data_processing.preprocess import (
    clean_data,
    map_binary_features,
    create_features,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_pipeline = None

# --- FIN DÉFINITION ---


def load_prediction_pipeline():
    """Charge la pipeline complète (preprocessor + modèle) depuis le disque."""
    global _pipeline
    if _pipeline is None:
        if not config.MODEL_PATH.exists():
            logger.error(f"Fichier pipeline non trouvé : {config.MODEL_PATH}")
            return None
        try:
            logger.info(f"Chargement de la pipeline depuis {config.MODEL_PATH}...")
            _pipeline = load(config.MODEL_PATH)
            logger.info("Pipeline chargée avec succès.")
        except Exception as e:
            logger.error(
                f"Erreur lors du chargement de la pipeline : {e}", exc_info=True
            )
            _pipeline = None
            return None
    return _pipeline


def predict_attrition(input_data: pd.DataFrame) -> Union[List[Dict], Dict]:
    """
    Fait une prédiction sur de nouvelles données brutes (DataFrame).
    Applique les transformations manuelles PUIS la pipeline sauvegardée.
    """
    pipeline = load_prediction_pipeline()
    if pipeline is None:
        return {"error": "Pipeline non chargée. Veuillez entraîner le modèle."}

    try:
        logger.info(f"Prédiction sur {len(input_data)} enregistrement(s)...")

        # --- ÉTAPE 1 : Appliquer les transformations manuelles ---
        # Note: clean_data attend 'a_quitte_l_entreprise', on doit l'ajouter
        # temporairement si elle n'y est pas, ou modifier clean_data.
        # Pour la prédiction, il est plus simple de ne pas l'exiger.
        # Modifions légèrement l'appel ou clean_data.
        # Ici, on suppose que clean_data peut fonctionner sans la cible,
        # ou on la modifie pour qu'elle puisse.
        # Pour l'instant, on ajoute une colonne 'bidon' pour que ça passe.
        if "a_quitte_l_entreprise" not in input_data.columns:
            input_data["a_quitte_l_entreprise"] = "Non"  # Valeur arbitraire

        df_cleaned = clean_data(input_data)
        df_mapped = map_binary_features(df_cleaned, config.BINARY_FEATURES_MAPPING)
        df_featured = create_features(df_mapped)

        # Enlever la colonne cible si on l'a ajoutée ou si elle était là
        X_predict = df_featured.drop(config.TARGET_VARIABLE, axis=1, errors="ignore")

        logger.info("Transformations manuelles appliquées.")

        # --- ÉTAPE 2 : Utiliser la pipeline complète pour prédire ---
        # La pipeline va maintenant appliquer le ColumnTransformer (scaling, OHE, etc.)
        # ET ensuite le classifier.
        probabilities = pipeline.predict_proba(X_predict)[:, 1]
        predictions = pipeline.predict(X_predict)

        results = []
        for i, index in enumerate(X_predict.index):
            results.append(
                {
                    "id_employe": index,
                    "probabilite_depart": float(probabilities[i]),
                    "prediction_depart": int(predictions[i]),
                }
            )
        logger.info("Prédiction terminée.")
        return results

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {e}", exc_info=True)
        return {"error": f"Erreur de prédiction: {e}"}


# Pour tester : poetry run python -m src.modeling.predict
if __name__ == "__main__":
    # Créez un exemple de données BRUTES (comme si elles venaient d'un nouveau formulaire ou BDD)
    # Doit contenir TOUTES les colonnes présentes dans les données avant le preprocessing.
    # Utilisez les mêmes noms que dans vos fichiers CSV initiaux.
    sample_data = pd.DataFrame(
        {
            "age": 45,
            "genre": "M",
            "revenu_mensuel": 4850,
            "statut_marital": "Célibataire",
            "departement": "Commercial",
            "poste": "Cadre Commercial",
            "nombre_experiences_precedentes": 8,
            "annees_dans_l_entreprise": 5,
            "satisfaction_employee_environnement": 4,
            "note_evaluation_precedente": 3,
            "satisfaction_employee_nature_travail": 3,
            "satisfaction_employee_equipe": 3,
            "satisfaction_employee_equilibre_pro_perso": 3,
            "note_evaluation_actuelle": 3,
            "heure_supplementaires": "Non",
            "augementation_salaire_precedente": 15,
            "nombre_participation_pee": 0,
            "nb_formations_suivies": 3,
            "distance_domicile_travail": 20,
            "niveau_education": 3,
            "domaine_etude": "Infra & Cloud",
            "frequence_deplacement": "Occasionnel",
            "annees_depuis_la_derniere_promotion": 0,
        },
        index=["EMP_TEST_1"],
    )  # Donner des index pour l'ID

    # Vérifier si le modèle existe avant de tester
    if config.MODEL_PATH.exists():
        predictions_output = predict_attrition(sample_data)
        print("\n--- Résultat de la Prédiction Test ---")
        print(predictions_output)
    else:
        print(
            f"\nModèle non trouvé à {config.MODEL_PATH}. Veuillez l'entraîner d'abord."
        )
