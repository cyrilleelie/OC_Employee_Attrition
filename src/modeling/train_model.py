import numpy as np
from joblib import dump
import logging

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression  # Ou RandomForestClassifier, etc.
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    fbeta_score,
    confusion_matrix,
)

from src.data_processing.load_data import get_data
# from src.data_processing.load_data import load_and_merge_csvs
from src.data_processing.preprocess import (
    clean_data,
    map_binary_features,
    create_features,
    build_preprocessor,
)
from src import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train_and_evaluate_pipeline():
    """
    Orchestre le chargement, la préparation, l'entraînement,
    l'évaluation et la sauvegarde de la pipeline ML.
    """
    logger.info(">>> Début du processus d'entraînement et d'évaluation <<<")

    # --- 1. Charger les données ---
    # df_raw = load_and_merge_csvs()
    df_featured = get_data(source="postgres")
    if df_featured is None:
        logger.error("Arrêt : Impossible de charger les données ou DataFrame vide.")
        return

    # --- 3. Appliquer les transformations "sûres" (avant split) ---
    # df_cleaned = clean_data(df_raw)
    # df_mapped = map_binary_features(df_cleaned, config.BINARY_FEATURES_MAPPING)
    # df_featured = create_features(df_mapped)

    df_for_training = df_featured.copy() # Ou df_featured si vous avez create_features

    # --- 3. Séparer X et y ET SUPPRIMER LES COLONNES NON-FEATURES DE X ---
    if config.TARGET_VARIABLE not in df_for_training.columns:
         raise ValueError(f"La colonne cible '{config.TARGET_VARIABLE}' n'est pas présente.")
    
    y = df_for_training[config.TARGET_VARIABLE]
    X = df_for_training.drop(config.TARGET_VARIABLE, axis=1)

    # Colonnes à exclure de X car ce ne sont pas des features pour le modèle
    # mais des identifiants ou des métadonnées de la BDD
    cols_to_exclude_from_features = [
        config.TARGET_VARIABLE, 
        'a_quitte_l_entreprise', # La version texte de la cible, si elle est encore là
        'id_employee',
        'date_creation_enregistrement', # Si elle vient de la BDD
        'date_derniere_modification'  # Si elle vient de la BDD
        # Ajoutez toute autre colonne qui ne doit pas être une feature
    ]
 
    X = df_for_training.drop(columns=[col for col in cols_to_exclude_from_features if col in df_for_training.columns], errors='ignore')
    logger.info(f"Colonnes dans X avant train_test_split (après exclusion): {X.columns.tolist()}")
    
    # --- 5. Séparer en Train / Test ---
    logger.info("Séparation des données en ensembles d'entraînement et de test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,  # Stratify est important pour les classes déséquilibrées
    )
    logger.info(f"Taille Train: {X_train.shape}, Taille Test: {X_test.shape}")

    # --- 6. Identifier les types de colonnes (basé sur X_train !) ---
    # C'est important de le faire sur X_train pour éviter toute fuite,
    # même si dans ce cas, c'est juste pour obtenir les listes de noms.
    potential_numerical_cols = X_train.select_dtypes(
        include=[np.number]
    ).columns.tolist()
    ordinal_to_encode = list(config.ORDINAL_FEATURES_CATEGORIES.keys())
    numerical_to_scale = [
        col for col in potential_numerical_cols if col not in ordinal_to_encode
    ]
    onehot_to_encode = X_train.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    # --- 7. Construire le préprocesseur (non ajusté) ---
    preprocessor = build_preprocessor(
        numerical_cols=numerical_to_scale,
        onehot_cols=onehot_to_encode,
        ordinal_cols=ordinal_to_encode,
        ordinal_categories=config.ORDINAL_FEATURES_CATEGORIES,
    )

    # --- 8. Définir le modèle ---
    # Ajoutez ici vos hyperparamètres optimisés si vous en avez.
    # L'utilisation de class_weight='balanced' est une première approche
    # pour gérer le déséquilibre. Vous pourriez intégrer SMOTE dans la pipeline
    # si nécessaire (en utilisant imblearn.pipeline.Pipeline).
    classifier = LogisticRegression(
        random_state=42, class_weight="balanced", max_iter=1000
    )

    # --- 9. Créer la Pipeline Complète ---
    full_pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", classifier)]
    )
    logger.info("Pipeline complète créée.")

    # --- 10. Entraîner la Pipeline Complète (sur X_train, y_train) ---
    # C'est ici que le 'fit' du preprocessor ET du classifier a lieu,
    # UNIQUEMENT sur les données d'entraînement.
    logger.info("Entraînement de la pipeline...")
    full_pipeline.fit(X_train, y_train)
    logger.info("Entraînement terminé.")

    # --- 11. Évaluer la Pipeline (sur X_test, y_test) ---
    logger.info("\n--- Évaluation sur le jeu de Test ---")
    y_pred = full_pipeline.predict(X_test)

    print("\nMatrice de Confusion :\n", confusion_matrix(y_test, y_pred))
    print(
        "\nRapport de Classification :\n",
        classification_report(y_test, y_pred, target_names=["Non", "Oui"]),
    )

    f2_scorer = fbeta_score(y_test, y_pred, beta=2)
    print(f"\nF2-Score (privilégie le Rappel) : {f2_scorer:.4f}")

    # --- 12. Sauvegarder la Pipeline Ajustée ---
    dump(full_pipeline, config.MODEL_PATH)
    logger.info(f"Pipeline complète et ajustée sauvegardée dans {config.MODEL_PATH}")
    logger.info(">>> Fin du processus <<<")


if __name__ == "__main__":
    train_and_evaluate_pipeline()
