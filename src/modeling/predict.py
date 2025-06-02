"""
Module pour charger la pipeline de Machine Learning entraînée et effectuer des prédictions.

Fonctions principales :
- `load_prediction_pipeline()`: Charge la pipeline Scikit-learn sauvegardée (modèle + préprocesseur).
- `predict_attrition()`: Prend des données brutes d'employés en entrée (DataFrame),
  applique les transformations de preprocessing initiales, puis utilise la pipeline
  chargée pour prédire la probabilité d'attrition et la classe de départ.
"""
import pandas as pd
from joblib import load
import logging
from typing import List, Dict, Union, Any # Ajout de Any

from src import config # Pour MODEL_PATH et BINARY_FEATURES_MAPPING
# Importer les fonctions de preprocessing nécessaires
from src.data_processing.preprocess import (
    clean_data,
    map_binary_features,
    create_features,
)

# Configuration du logging pour ce module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Variable globale pour stocker la pipeline chargée et éviter de la recharger à chaque appel
_pipeline: Any = None # Utilisation de Any car le type exact de la pipeline peut être complexe


def load_prediction_pipeline() -> Any | None:
    """
    Charge la pipeline de prédiction complète (préprocesseur + modèle) depuis le disque.

    La pipeline est chargée une seule fois et stockée dans une variable globale `_pipeline`
    pour optimiser les appels suivants.

    Returns:
        Pipeline | None: L'objet pipeline Scikit-learn chargé, ou None si une erreur
                         se produit (ex: fichier non trouvé, erreur de chargement).
    """
    global _pipeline
    if _pipeline is None: # Charger seulement si pas déjà en mémoire
        if not config.MODEL_PATH.exists():
            logger.error(f"Fichier pipeline non trouvé à l'emplacement configuré : {config.MODEL_PATH}")
            return None
        try:
            logger.info(f"Chargement de la pipeline de prédiction depuis : {config.MODEL_PATH}...")
            _pipeline = load(config.MODEL_PATH)
            logger.info("Pipeline de prédiction chargée avec succès.")
        except Exception as e:
            logger.error(
                f"Erreur critique lors du chargement de la pipeline : {e}", exc_info=True
            )
            _pipeline = None # S'assurer que _pipeline est None en cas d'échec
            return None
    return _pipeline


def predict_attrition(input_data: pd.DataFrame) -> Union[List[Dict[str, Any]], Dict[str, str]]:
    """
    Prédit le risque d'attrition pour les employés fournis en entrée.

    Cette fonction prend un DataFrame de données brutes, applique les étapes
    de preprocessing initiales (nettoyage, mappage binaire, création de features)
    puis utilise la pipeline Scikit-learn entraînée et chargée pour effectuer
    les prédictions.

    Args:
        input_data (pd.DataFrame): DataFrame contenant les données brutes des employés
                                   pour lesquels faire une prédiction. Les colonnes doivent
                                   correspondre aux attentes de `clean_data` et
                                   `map_binary_features` (format brut).

    Returns:
        Union[List[Dict[str, Any]], Dict[str, str]]:
            - Une liste de dictionnaires si la prédiction réussit, chaque dictionnaire
              contenant 'id_employe', 'probabilite_depart', 'prediction_depart'.
            - Un dictionnaire d'erreur `{"error": "message"}` si la pipeline n'est pas
              chargée ou si une autre erreur majeure se produit.
    """
    pipeline = load_prediction_pipeline()
    if pipeline is None:
        # Le logger dans load_prediction_pipeline aura déjà enregistré l'erreur spécifique.
        return {"error": "Pipeline de prédiction non chargée. Le modèle n'a peut-être pas été entraîné ou le fichier est manquant."}

    try:
        logger.info(f"Début de la prédiction pour {len(input_data)} enregistrement(s)...")
        
        # Travailler sur une copie pour éviter de modifier le DataFrame original
        data_to_process = input_data.copy()

        # --- ÉTAPE 1 : Appliquer les transformations manuelles ---
        # clean_data s'attend à la colonne 'a_quitte_l_entreprise' pour créer config.TARGET_VARIABLE.
        # Pour la prédiction, cette colonne n'existe pas dans les données d'entrée.
        # Nous ajoutons une colonne factice 'a_quitte_l_entreprise' pour que clean_data
        # puisse s'exécuter sans erreur. Cette colonne sera ensuite supprimée.
        if "a_quitte_l_entreprise" not in data_to_process.columns:
            data_to_process["a_quitte_l_entreprise"] = "Non" # Valeur factice, n'influence pas les features
            logger.debug("Colonne 'a_quitte_l_entreprise' factice ajoutée pour le preprocessing.")

        df_cleaned = clean_data(data_to_process)
        # Utiliser le mapping centralisé depuis config.py
        df_mapped = map_binary_features(df_cleaned, config.BINARY_FEATURES_MAPPING)
        df_featured = create_features(df_mapped)

        # Préparer X_predict : supprimer la variable cible (même factice) et toute autre
        # colonne qui ne fait pas partie des features attendues par la pipeline.
        # La pipeline a été entraînée sur un X qui n'incluait pas config.TARGET_VARIABLE.
        cols_to_drop_for_predict = [config.TARGET_VARIABLE]
        # Si d'autres colonnes comme 'id_employee' sont présentes dans df_featured mais que la pipeline
        # ne les attend pas comme features (ce qui est le cas si elles ont été droppées avant le fit
        # du preprocessor dans train_model.py), il faudrait les lister ici aussi.
        # Cependant, le ColumnTransformer avec remainder='drop' devrait ignorer les colonnes inconnues.
        # Mais c'est plus propre de présenter à la pipeline exactement ce qu'elle a vu à l'entraînement.
        # X_predict = df_featured.drop(columns=[col for col in cols_to_drop_for_predict if col in df_featured.columns], errors="ignore")
        
        # En se basant sur train_model.py, X_predict ne doit pas contenir TARGET_VARIABLE.
        # Les autres colonnes non-features (comme id_employee) ont été retirées AVANT
        # la définition des listes de colonnes pour build_preprocessor, donc le preprocessor ne les attend pas.
        if config.TARGET_VARIABLE in df_featured.columns:
            X_predict = df_featured.drop(config.TARGET_VARIABLE, axis=1)
        else:
            X_predict = df_featured # Si TARGET_VARIABLE n'a pas été créé (ex: clean_data modifié)
        
        logger.info(f"Transformations manuelles appliquées. Shape de X_predict: {X_predict.shape}")
        # logger.debug(f"Colonnes de X_predict avant la pipeline : {X_predict.columns.tolist()}")


        # --- ÉTAPE 2 : Utiliser la pipeline complète pour prédire ---
        logger.info("Application de la pipeline Scikit-learn pour la prédiction...")
        probabilities = pipeline.predict_proba(X_predict)[:, 1]
        predictions = pipeline.predict(X_predict)
        logger.info("Calcul des probabilités et des classes terminé.")

        results = []
        for i, index_val in enumerate(X_predict.index): # Renommé index en index_val pour éviter conflit
            results.append(
                {
                    "id_employe": index_val, # Utilise l'index du DataFrame d'entrée
                    "probabilite_depart": float(probabilities[i]),
                    "prediction_depart": int(predictions[i]),
                }
            )
        logger.info("Prédictions formatées avec succès.")
        return results

    except Exception as e:
        logger.error(f"Erreur critique lors du processus de prédiction : {e}", exc_info=True)
        return {"error": f"Erreur de prédiction : {str(e)}"}


# Pour tester ce module : poetry run python -m src.modeling.predict
if __name__ == "__main__":
    logger.info("--- Test direct du module predict.py ---")
    # Exemple de données brutes (doit correspondre au schéma EmployeeInput de l'API)
    sample_data_dict = {
        # Assurez-vous que toutes les clés correspondent à EmployeeInput et aux attentes de clean_data
        "age": [45, 30],
        "genre": ["M", "F"], # Utiliser les valeurs textuelles brutes
        "revenu_mensuel": [4850, 6000],
        "statut_marital": ["Célibataire", "Marié(e)"],
        "departement": ["Commercial", "R&D"],
        "poste": ["Cadre Commercial", "Ingenieur"],
        "nombre_experiences_precedentes": [8, 5],
        "annees_dans_l_entreprise": [5, 2],
        "satisfaction_employee_environnement": [4,3],
        "note_evaluation_precedente": [3,4],
        "satisfaction_employee_nature_travail": [3,2],
        "satisfaction_employee_equipe": [3,4],
        "satisfaction_employee_equilibre_pro_perso": [3,2],
        "note_evaluation_actuelle": [3,4],
        "heure_supplementaires": ["Non", "Oui"], # Valeurs textuelles brutes
        "augementation_salaire_precedente": ["15 %", "10 %"], # Format texte brut
        "nombre_participation_pee": [0,1],
        "nb_formations_suivies": [3,1],
        "distance_domicile_travail": [20,5],
        "niveau_education": ["Bac+3", "Bac+5"], # Exemple, adaptez à vos données
        "domaine_etude": ["Infra & Cloud", "Developpement"],
        "frequence_deplacement": ["Occasionnel", "Frequent"], # Exemple, adaptez
        "annees_depuis_la_derniere_promotion": [0,1],
        # Pas besoin de 'a_quitte_l_entreprise' ici, la fonction predict_attrition l'ajoute temporairement
    }
    sample_df = pd.DataFrame(sample_data_dict, index=["EMP_TEST_A", "EMP_TEST_B"])

    if config.MODEL_PATH.exists():
        logger.info("Modèle trouvé, lancement de la prédiction test...")
        predictions_output = predict_attrition(sample_df)
        print("\n--- Résultat de la Prédiction Test ---")
        if isinstance(predictions_output, dict) and "error" in predictions_output:
            print(f"Erreur: {predictions_output['error']}")
        else:
            for res in predictions_output:
                print(res)
    else:
        print(
            f"\nModèle non trouvé à {config.MODEL_PATH}. Veuillez l'entraîner d'abord avec train_model.py."
        )
    logger.info("--- Fin du test direct du module predict.py ---")