"""
Module d'entraînement et d'évaluation du modèle de prédiction d'attrition.

Ce script orchestre le pipeline complet de Machine Learning :
1. Chargement des données prétraitées depuis la source configurée (PostgreSQL).
2. (Optionnel) Création de features supplémentaires.
3. Séparation des données en ensembles d'entraînement et de test.
4. Identification des types de colonnes pour le preprocessing.
5. Construction d'une pipeline Scikit-learn incluant :
    - Un préprocesseur (ColumnTransformer) pour imputer, scaler (numériques)
      et encoder (catégorielles OneHot et Ordinal).
    - Un classifieur (actuellement LogisticRegression).
6. Entraînement de la pipeline complète sur les données d'entraînement.
7. Évaluation du modèle sur les données de test (Matrice de confusion, rapport de
   classification, F2-score).
8. Sauvegarde de la pipeline entraînée pour une utilisation ultérieure (prédictions).
"""
import numpy as np
from joblib import dump # Pour sauvegarder la pipeline
import logging

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    fbeta_score,
    confusion_matrix,
)

# Fonctions et configurations importées des autres modules du projet
from src.data_processing.load_data import get_data
from src.data_processing.preprocess import (
    create_features, # Utilisé pour la création de features à la volée
    build_preprocessor, # Pour construire le ColumnTransformer
)
from src import config # Pour TARGET_VARIABLE, ORDINAL_FEATURES_CATEGORIES, MODEL_PATH

# Configuration du logging pour ce module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train_and_evaluate_pipeline():
    """
    Orchestre le chargement des données, la préparation, l'entraînement d'un modèle
    de classification, son évaluation, et la sauvegarde de la pipeline entraînée.

    Cette fonction est le point d'entrée principal pour le processus d'entraînement.
    Elle utilise les configurations définies dans `config.py` et les fonctions
    de `load_data.py` et `preprocess.py`.

    Le modèle actuel est une Régression Logistique, et la métrique principale
    d'évaluation est le F2-score pour la classe positive (départ d'employé).

    Raises:
        ValueError: Si la colonne cible n'est pas trouvée dans les données
                    après les étapes initiales de chargement et de feature engineering.
    """
    logger.info(">>> Début du processus d'entraînement et d'évaluation du modèle <<<")

    # --- 1. Charger les données ---
    logger.info("Étape 1: Chargement des données depuis la source configurée (PostgreSQL).")
    df_loaded = get_data(source="postgres")
    if df_loaded is None or df_loaded.empty:
        logger.error("Arrêt : Impossible de charger les données ou DataFrame vide depuis la source.")
        return

    # --- 2. Création de Features (si applicable) ---
    # Cette étape applique la fonction create_features pour toute ingénierie de features
    # qui n'aurait pas été faite avant le stockage en base, ou qui est spécifique à l'entraînement.
    logger.info("Étape 2: Application de la création de features (si définie).")
    df_featured = create_features(df_loaded)

    if df_featured.empty:
        logger.error("Arrêt : DataFrame vide après l'étape de création de features.")
        return

    df_for_training = df_featured.copy() # Utiliser une copie pour les modifications suivantes

    # --- 3. Vérification et Séparation de la Cible (y) et des Features (X) ---
    logger.info("Étape 3: Séparation des features (X) et de la variable cible (y).")
    if config.TARGET_VARIABLE not in df_for_training.columns:
        logger.error(f"La colonne cible '{config.TARGET_VARIABLE}' est introuvable dans le DataFrame.")
        raise ValueError(
            f"La colonne cible '{config.TARGET_VARIABLE}' n'est pas présente dans les données chargées."
        )
    
    y = df_for_training[config.TARGET_VARIABLE]
    
    # Exclure la cible et les colonnes non-feature de X
    cols_to_exclude_from_features = [
        config.TARGET_VARIABLE,
        "a_quitte_l_entreprise",  # Version texte originale de la cible, si présente
        "id_employee",            # Identifiant, non utilisé comme feature
        "date_creation_enregistrement",
        "date_derniere_modification"
        # Ajoutez d'autres colonnes à exclure si nécessaire
    ]
    
    X = df_for_training.drop(
        columns=[col for col in cols_to_exclude_from_features if col in df_for_training.columns],
        errors="ignore" # ignore si une colonne de la liste n'est pas trouvée dans df_for_training
    )
    logger.info(
        f"Nombre de features initiales dans X avant train_test_split : {len(X.columns)}"
    )
    # logger.debug(f"Colonnes dans X : {X.columns.tolist()}") # Décommentez pour débogage détaillé

    # --- 4. Séparation en Ensembles d'Entraînement et de Test ---
    logger.info("Étape 4: Séparation des données en ensembles d'entraînement et de test (80%/20%).")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20, # 20% des données pour le test
        random_state=42, # Pour la reproductibilité
        stratify=y,     # Maintient la proportion des classes dans les deux ensembles
    )
    logger.info(f"Dimensions de l'ensemble d'entraînement - X_train: {X_train.shape}, y_train: {y_train.shape}")
    logger.info(f"Dimensions de l'ensemble de test - X_test: {X_test.shape}, y_test: {y_test.shape}")

    # --- 5. Identification des Types de Colonnes pour le Préprocessing (basé sur X_train) ---
    logger.info("Étape 5: Identification des types de colonnes pour le préprocessing (sur X_train).")
    potential_numerical_cols = X_train.select_dtypes(
        include=[np.number]
    ).columns.tolist()
    ordinal_to_encode = list(config.ORDINAL_FEATURES_CATEGORIES.keys()) # Colonnes définies comme ordinales
    
    # Les colonnes numériques à scaler sont celles qui sont numériques et non ordinales
    numerical_to_scale = [
        col for col in potential_numerical_cols if col not in ordinal_to_encode
    ]
    # Les colonnes pour OneHotEncoding sont celles de type object/category qui ne sont pas ordinales
    onehot_to_encode = [
        col for col in X_train.select_dtypes(include=["object", "category"]).columns.tolist()
        if col not in ordinal_to_encode
    ]
    logger.info(f"Colonnes numériques à scaler : {numerical_to_scale}")
    logger.info(f"Colonnes pour OneHotEncoding : {onehot_to_encode}")
    logger.info(f"Colonnes pour OrdinalEncoding : {ordinal_to_encode}")

    # --- 6. Construction du Préprocesseur ---
    logger.info("Étape 6: Construction du préprocesseur Scikit-learn.")
    preprocessor = build_preprocessor(
        numerical_cols=numerical_to_scale,
        onehot_cols=onehot_to_encode,
        ordinal_cols=ordinal_to_encode,
        ordinal_categories_map=config.ORDINAL_FEATURES_CATEGORIES, # Le nom du paramètre a été harmonisé
    )

    # --- 7. Définition du Modèle de Classification ---
    logger.info("Étape 7: Définition du modèle (LogisticRegression).")
    classifier = LogisticRegression(
        random_state=42, class_weight="balanced", max_iter=1000
    )

    # --- 8. Création de la Pipeline Complète (Préprocesseur + Classifieur) ---
    logger.info("Étape 8: Création de la pipeline Scikit-learn complète.")
    full_pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", classifier)]
    )
    logger.info("Pipeline complète créée.")

    # --- 9. Entraînement de la Pipeline Complète ---
    logger.info("Étape 9: Entraînement de la pipeline sur l'ensemble d'entraînement...")
    full_pipeline.fit(X_train, y_train)
    logger.info("Entraînement de la pipeline terminé.")

    # --- 10. Évaluation de la Pipeline sur l'Ensemble de Test ---
    logger.info("Étape 10: Évaluation de la pipeline sur l'ensemble de test...")
    y_pred = full_pipeline.predict(X_test)
    # y_pred_proba = full_pipeline.predict_proba(X_test)[:, 1] # Gardé pour référence, mais non utilisé actuellement

    logger.info("\n--- Résultats de l'Évaluation sur le Jeu de Test ---")
    print("\nMatrice de Confusion :\n", confusion_matrix(y_test, y_pred))
    print(
        "\nRapport de Classification :\n",
        classification_report(y_test, y_pred, target_names=["Non", "Oui"]),
    )

    f2_scorer = fbeta_score(y_test, y_pred, beta=2, zero_division=0) # Ajout de zero_division pour éviter warning/erreur
    print(f"\nF2-Score (privilégie le Rappel pour la classe 'Oui') : {f2_scorer:.4f}")

    # --- 11. Sauvegarde de la Pipeline Ajustée ---
    logger.info("Étape 11: Sauvegarde de la pipeline entraînée...")
    try:
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True) # S'assurer que le dossier existe
        dump(full_pipeline, config.MODEL_PATH)
        logger.info(f"Pipeline complète et ajustée sauvegardée dans : {config.MODEL_PATH}")
    except Exception as e_save:
        logger.error(f"Erreur lors de la sauvegarde de la pipeline : {e_save}", exc_info=True)


    logger.info(">>> Fin du processus d'entraînement et d'évaluation <<<")


if __name__ == "__main__":
    train_and_evaluate_pipeline()