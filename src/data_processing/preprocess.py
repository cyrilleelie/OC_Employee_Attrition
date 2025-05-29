import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from src import config
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def map_binary_features(df: pd.DataFrame, binary_cols_map: dict) -> pd.DataFrame:
    """Mappe les colonnes binaires spécifiées en 0 et 1."""
    df = df.copy()
    logger.info("Mappage des features binaires...")
    for col, mapping in binary_cols_map.items():
        if col in df.columns:
            # S'assurer que les valeurs sont bien des strings avant de mapper si nécessaire
            df[col] = df[col].astype(str).map(mapping)
            logger.info(f"Colonne '{col}' mappée en binaire.")
            # Vérifier si des NaN ont été introduits (signe d'un problème de mapping)
            nan_count = df[col].isnull().sum()
            if nan_count > 0:
                logger.warning(
                    f"{nan_count} valeurs dans '{col}' n'ont pas pu être mappées et sont devenues NaN."
                )
                # Option: Imputer ici ou laisser SimpleImputer le gérer plus tard
                # df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 0)
        else:
            logger.warning(f"Colonne binaire '{col}' non trouvée.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Applique les étapes de nettoyage et de conversion de type."""
    logger.info("Nettoyage des données...")
    df = df.copy()

    if "a_quitte_l_entreprise" in df.columns:
        df[config.TARGET_VARIABLE] = df["a_quitte_l_entreprise"].map(
            {"Oui": 1, "Non": 0}
        )
        logger.info(f"Colonne '{config.TARGET_VARIABLE}' créée.")
    else:
        logger.error("La colonne 'a_quitte_l_entreprise' est manquante.")
        raise ValueError("Colonne cible manquante.")

    cols_to_drop = [
        "id_employee",
        "nombre_heures_travailless",
        "eval_number",
        "nombre_employee_sous_responsabilite",
        "code_sondage",
        "ayant_enfants",
        "a_quitte_l_entreprise",
        "annee_experience_totale",
        "niveau_hierarchique_poste",
        "annees_dans_le_poste_actuel",
        "annes_sous_responsable_actuel",
    ]
    df = df.drop(
        columns=[col for col in cols_to_drop if col in df.columns], errors="ignore"
    )
    logger.info(f"Colonnes supprimées (si présentes) : {cols_to_drop}")

    initial_rows = len(df)
    df = df.drop_duplicates()
    if len(df) < initial_rows:
        logger.info(f"{initial_rows - len(df)} lignes dupliquées supprimées.")

    col_aug = "augementation_salaire_precedente"  # Mettez le nom exact
    if col_aug in df.columns:
        logger.info(f"Conversion de '{col_aug}' en numérique...")
        df[col_aug] = df[col_aug].astype(str).str.replace(" %", "", regex=False)
        df[col_aug] = pd.to_numeric(df[col_aug], errors="coerce")
        nan_count = df[col_aug].isnull().sum()
        if nan_count > 0:
            logger.warning(f"{nan_count} valeurs dans '{col_aug}' sont devenues NaN.")
        logger.info(f"'{col_aug}' convertie avec succès.")
    else:
        logger.warning(
            f"La colonne '{col_aug}' n'a pas été trouvée pour la conversion."
        )

    logger.info("Nettoyage terminé.")
    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Crée de nouvelles features."""
    logger.info("Création de features...")
    df = df.copy()
    # --- AJOUTEZ VOS FEATURES ICI ---
    logger.info("Création de features terminée.")
    return df


def build_preprocessor(
    numerical_cols: list,
    onehot_cols: list,
    ordinal_cols: list,
    ordinal_categories: dict,
) -> ColumnTransformer:
    """Construit la pipeline de preprocessing Sklearn."""
    logger.info("Construction du préprocesseur Sklearn...")
    transformers_list = []

    if numerical_cols:
        numerical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        transformers_list.append(("num", numerical_transformer, numerical_cols))

    if onehot_cols:
        onehot_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore", sparse_output=False, drop="first"
                    ),
                ),
            ]
        )
        transformers_list.append(("onehot", onehot_transformer, onehot_cols))

    if ordinal_cols:
        for col in ordinal_cols:
            if col not in ordinal_categories:
                raise ValueError(f"Les catégories pour '{col}' ne sont pas définies.")
            categories_for_col = [ordinal_categories[col]]
            ordinal_transformer_col = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    (
                        "ordinal",
                        OrdinalEncoder(
                            categories=categories_for_col,
                            handle_unknown="use_encoded_value",
                            unknown_value=-1,
                        ),
                    ),
                ]
            )
            transformers_list.append((f"ord_{col}", ordinal_transformer_col, [col]))

    if not transformers_list:
        logger.warning("Aucune colonne spécifiée. Préprocesseur vide.")
        return ColumnTransformer(transformers=[], remainder="passthrough")

    preprocessor = ColumnTransformer(transformers=transformers_list, remainder="drop")
    logger.info("Préprocesseur Sklearn construit.")
    return preprocessor


def run_preprocessing_pipeline(
    df: pd.DataFrame,
    binary_cols_map: dict = None,
    ordinal_cols_categories: dict = None,
    preprocessor: ColumnTransformer = None,
    fit: bool = False,
):
    """Exécute le pipeline de preprocessing complet."""
    df_clean = clean_data(df)

    if binary_cols_map:
        df_clean = map_binary_features(df_clean, binary_cols_map)

    df_featured = create_features(df_clean)

    if config.TARGET_VARIABLE not in df_featured.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET_VARIABLE}' n'est pas présente."
        )

    y = df_featured[config.TARGET_VARIABLE]
    X = df_featured.drop(config.TARGET_VARIABLE, axis=1)

    ordinal_to_encode = (
        list(ordinal_cols_categories.keys()) if ordinal_cols_categories else []
    )

    potential_numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    # Les colonnes numériques incluent maintenant les binaires mappées.
    # On enlève les ordinales, car elles seront traitées séparément (même si numériques).
    numerical_to_scale = [
        col for col in potential_numerical_cols if col not in ordinal_to_encode
    ]

    onehot_to_encode = [
        col
        for col in X.select_dtypes(include=["object", "category"]).columns.tolist()
        if col not in ordinal_to_encode
    ]

    for col in ordinal_to_encode:
        if col not in X.columns:
            raise ValueError(f"La colonne ordinale '{col}' spécifiée n'existe pas.")

    logger.info(f"Colonnes numériques à scaler : {numerical_to_scale}")
    logger.info(f"Colonnes catégorielles pour OneHotEncoding : {onehot_to_encode}")
    logger.info(f"Colonnes catégorielles pour OrdinalEncoding : {ordinal_to_encode}")

    if fit:
        processor_instance = build_preprocessor(
            numerical_to_scale,
            onehot_to_encode,
            ordinal_to_encode,
            ordinal_cols_categories or {},
        )
        logger.info("Ajustement (fit) et transformation des données...")
        X_processed = processor_instance.fit_transform(X)
        try:
            feature_names = processor_instance.get_feature_names_out()
        except Exception as e:
            logger.warning(
                f"Impossible d'obtenir les noms de features: {e}. Noms génériques utilisés."
            )
            feature_names = [f"feature_{i}" for i in range(X_processed.shape[1])]
        logger.info("Transformation terminée.")
        return (
            pd.DataFrame(X_processed, columns=feature_names, index=X.index),
            y,
            processor_instance,
        )
    else:
        if preprocessor:
            logger.info("Transformation des données (sans ajustement)...")
            X_processed = preprocessor.transform(X)
            try:
                feature_names = preprocessor.get_feature_names_out()
            except Exception as e:
                logger.warning(
                    f"Impossible d'obtenir les noms de features: {e}. Noms génériques utilisés."
                )
                feature_names = [f"feature_{i}" for i in range(X_processed.shape[1])]
            logger.info("Transformation terminée.")
            return pd.DataFrame(X_processed, columns=feature_names, index=X.index), y
        else:
            raise ValueError("Un preprocessor doit être fourni si fit=False.")


# Pour tester : poetry run python -m src.data_processing.preprocess
if __name__ == "__main__":
    from .load_data import load_and_merge_csvs

    df_raw = load_and_merge_csvs()

    if df_raw is not None:
        # --- CONFIGURATION SPÉCIFIQUE À VOS DONNÉES (À ADAPTER ABSOLUMENT) ---
        binary_features_mapping = {
            "genre": {"M": 0, "F": 1},  # Adaptez si 'Masculin'/'Féminin' etc.
            "heure_supplementaires": {
                "Non": 0,
                "Oui": 1,
            },  # <-- AJOUTÉ ICI ! Adaptez 'Non'/'Oui' si nécessaire.
        }
        ordinal_features_categories = {
            "frequence_deplacement": ["Aucun", "Occasionnel", "Frequent"],
        }
        # --- FIN CONFIGURATION SPÉCIFIQUE ---

        try:
            X_p, y_p, proc = run_preprocessing_pipeline(
                df_raw,
                binary_cols_map=binary_features_mapping,
                ordinal_cols_categories=ordinal_features_categories,
                fit=True,
            )
            print("\n--- Preprocessing Réussi ---")
            print("Shape X_processed:", X_p.shape)
            print("X_processed (head):")
            print(X_p.head())

            # Vérifier que les colonnes binaires sont bien numériques et scalées
            genre_col = [col for col in X_p.columns if "genre" in col]
            hs_col = [col for col in X_p.columns if "heure_supplementaires" in col]

            if genre_col:
                print(f"\nColonne 'genre' traitée (scalée) : {genre_col[0]}")
            if hs_col:
                print(f"Colonne 'heure_supplementaires' traitée (scalée) : {hs_col[0]}")

        except Exception as e:
            print("\n--- Erreur lors du preprocessing ---")
            print(e)
            import traceback

            traceback.print_exc()
