# Dans src/data_processing/preprocess.py
"""
Module de prétraitement des données pour le projet d'attrition RH.

Ce module contient les fonctions nécessaires pour :
- Mapper les features binaires.
- Nettoyer les données brutes (conversion de la cible, suppression de colonnes,
  gestion des doublons, conversion de types spécifiques comme les pourcentages).
- Créer de nouvelles features (feature engineering) - actuellement un placeholder.
- Construire une pipeline de prétraitement Scikit-learn (ColumnTransformer) pour
  l'imputation, la mise à l'échelle des numériques, et l'encodage des catégorielles
  (OneHot et Ordinal).
- Exécuter l'ensemble de ce pipeline de preprocessing.
"""
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from src import config # Pour config.TARGET_VARIABLE, config.BINARY_FEATURES_MAPPING, etc.
import logging
import numpy as np # Pour np.number lors de la sélection de dtypes

# Configuration du logging pour ce module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def map_binary_features(df: pd.DataFrame, binary_cols_map: dict) -> pd.DataFrame:
    """
    Mappe les valeurs des colonnes catégorielles binaires spécifiées en 0 et 1.

    Args:
        df (pd.DataFrame): DataFrame d'entrée.
        binary_cols_map (dict): Dictionnaire où les clés sont les noms de colonnes
                                et les valeurs sont des dictionnaires de mapping
                                (ex: {'Oui': 1, 'Non': 0}).

    Returns:
        pd.DataFrame: DataFrame avec les colonnes binaires mappées.
    """
    df = df.copy() # Évite les SettingWithCopyWarning
    logger.info("Application du mappage sur les features binaires...")
    for col, mapping in binary_cols_map.items():
        if col in df.columns:
            # Assurer que la colonne est de type string avant d'appliquer .map
            # Cela évite des erreurs si une colonne est déjà numérique (ex: 0/1)
            # ou contient des types mixtes.
            df[col] = df[col].astype(str).map(mapping)
            # Après .map, les valeurs non trouvées dans le mapping deviennent NaN.
            # Il est important que ces NaN soient de type float pour que SimpleImputer (numérique) fonctionne.
            # Si la colonne originale était object et contenait des strings et des NaN après map,
            # SimpleImputer(strategy='most_frequent') fonctionnerait mais SimpleImputer(strategy='median') échouerait.
            # Le plus sûr est de convertir en type numérique si on s'attend à 0 et 1.
            df[col] = pd.to_numeric(df[col], errors='coerce') # Convertit en float, les erreurs (anciens NaN) restent NaN

            logger.info(f"Colonne '{col}' mappée en binaire numérique.")
            
            nan_count = df[col].isnull().sum()
            if nan_count > 0:
                logger.warning(
                    f"{nan_count} valeur(s) dans la colonne '{col}' n'ont pas pu être mappée(s) "
                    f"correctement et sont devenue(s) NaN (ou étaient déjà NaN)."
                )
        else:
            logger.warning(f"Colonne binaire '{col}' spécifiée pour mappage mais non trouvée dans le DataFrame.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique les étapes de nettoyage de base et les conversions de types spécifiques.

    - Convertit la variable cible textuelle en format numérique.
    - Supprime les colonnes jugées inutiles ou redondantes.
    - Supprime les lignes dupliquées.
    - Convertit la colonne 'augementation_salaire_precedente' (texte en "XX %") en numérique.

    Args:
        df (pd.DataFrame): DataFrame d'entrée brut ou fusionné.

    Returns:
        pd.DataFrame: DataFrame nettoyé.

    Raises:
        ValueError: Si la colonne cible 'a_quitte_l_entreprise' est manquante.
    """
    logger.info("Début du nettoyage des données...")
    df = df.copy()

    # Conversion de la variable cible
    if "a_quitte_l_entreprise" in df.columns:
        df[config.TARGET_VARIABLE] = df["a_quitte_l_entreprise"].map(
            {"Oui": 1, "Non": 0}
        )
        # Convertir en type entier nullable pour gérer les NaN si map échoue pour certaines valeurs
        df[config.TARGET_VARIABLE] = pd.to_numeric(df[config.TARGET_VARIABLE], errors='coerce').astype('Int64')
        logger.info(f"Colonne cible '{config.TARGET_VARIABLE}' créée et convertie en Int64.")
    else:
        # Pour la prédiction, cette colonne ne sera pas présente.
        # On ne devrait pas lever d'erreur si on est en mode prédiction.
        # Cette fonction est appelée par run_preprocessing_pipeline qui sépare X et y *après*.
        # Et aussi par populate_db qui a besoin de la cible.
        # Pour predict.py, on ajoute une colonne factice 'a_quitte_l_entreprise'.
        # Donc, cette condition est surtout pour la robustesse lors de l'entraînement.
        logger.warning("La colonne 'a_quitte_l_entreprise' est manquante. Si c'est pour la prédiction, c'est normal.")
        # Si cette fonction est appelée par un flux où la cible DOIT être là (comme populate_db ou train_model avant split X/y)
        # alors une erreur est appropriée.
        # Pour l'instant, on logue un warning, le check de présence de TARGET_VARIABLE se fera plus tard.


    # Liste des colonnes à supprimer (adaptez si nécessaire)
    # 'id_employee' est conservé pour le moment, car il est utilisé par populate_db
    # et sera explicitement retiré de X dans train_model.py avant l'entraînement.
    cols_to_drop = [
        "nombre_heures_travailless", # Semble être une coquille (s en trop)
        "eval_number",
        "nombre_employee_sous_responsabilite",
        "code_sondage",
        "ayant_enfants",
        "a_quitte_l_entreprise", # Version texte de la cible, une fois la version numérique créée
        "annee_experience_totale", # Supposée redondante ou moins pertinente
        "niveau_hierarchique_poste", # Supposée redondante ou moins pertinente
        "annees_dans_le_poste_actuel", # Supposée redondante ou moins pertinente
        "annes_sous_responsable_actuel", # Coquille "annes" -> "annees" ?
    ]
    actual_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    if actual_cols_to_drop:
        df = df.drop(columns=actual_cols_to_drop, errors="ignore")
        logger.info(f"Colonnes supprimées : {actual_cols_to_drop}")
    else:
        logger.info("Aucune colonne de la liste `cols_to_drop` n'a été trouvée pour suppression.")


    # Suppression des doublons
    initial_rows = len(df)
    df = df.drop_duplicates()
    if len(df) < initial_rows:
        logger.info(f"{initial_rows - len(df)} lignes dupliquées supprimées.")

    # Conversion de 'augementation_salaire_precedente'
    col_aug = "augementation_salaire_precedente"
    if col_aug in df.columns:
        logger.info(f"Conversion de la colonne '{col_aug}' en numérique...")
        df[col_aug] = df[col_aug].astype(str).str.replace(" %", "", regex=False).str.strip()
        df[col_aug] = pd.to_numeric(df[col_aug], errors="coerce")
        nan_count = df[col_aug].isnull().sum()
        if nan_count > 0:
            logger.warning(
                f"{nan_count} valeur(s) dans '{col_aug}' n'ont pas pu être converties "
                f"en numérique et sont devenue(s) NaN."
            )
        logger.info(f"Colonne '{col_aug}' convertie avec succès en type numérique.")
    else:
        logger.warning(
            f"La colonne '{col_aug}' n'a pas été trouvée pour la conversion numérique."
        )

    logger.info("Nettoyage des données terminé.")
    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée de nouvelles features (ingénierie des features) à partir des colonnes existantes.

    Args:
        df (pd.DataFrame): DataFrame d'entrée (généralement après nettoyage et mappage binaire).

    Returns:
        pd.DataFrame: DataFrame avec les nouvelles features ajoutées.
    """
    logger.info("Début de la création de features...")
    df = df.copy()

    # --- EXEMPLE DE FEATURE A AJOUTER ---
    # Si vous voulez ajouter une feature 'satisfaction_moyenne' basée sur les colonnes Q_...
    # sondage_cols = [col for col in df.columns if col.startswith('Q_') and col not in ['Q_satisfaction_generale']]
    # if sondage_cols:
    #     df['satisfaction_moyenne_autres_sondages'] = df[sondage_cols].mean(axis=1, skipna=True)
    #     logger.info("Feature 'satisfaction_moyenne_autres_sondages' créée.")
    # else:
    #     logger.info("Aucune colonne de sondage (Q_...) trouvée pour calculer 'satisfaction_moyenne_autres_sondages'.")

    # Pour l'instant, cette fonction ne fait rien de plus.
    # Vous pouvez ajouter ici la logique de création de features que vous aviez dans vos notebooks.
    logger.info("Création de features terminée (actuellement, pas de nouvelles features implémentées).")
    return df


def build_preprocessor(
    numerical_cols: list,
    onehot_cols: list,
    ordinal_cols: list,
    ordinal_categories_map: dict, # Renommé pour correspondre à l'usage dans la fct
) -> ColumnTransformer:
    """
    Construit et retourne un objet ColumnTransformer de Scikit-learn pour le prétraitement.

    Le ColumnTransformer applique :
    - Imputation par la médiane puis StandardScaler aux colonnes numériques.
    - Imputation par la valeur la plus fréquente puis OneHotEncoder aux colonnes catégorielles nominales.
    - Imputation par la valeur la plus fréquente puis OrdinalEncoder aux colonnes catégorielles ordinales.

    Args:
        numerical_cols (list): Liste des noms des colonnes numériques.
        onehot_cols (list): Liste des noms des colonnes catégorielles à encoder en One-Hot.
        ordinal_cols (list): Liste des noms des colonnes catégorielles ordinales.
        ordinal_categories_map (dict): Dictionnaire spécifiant l'ordre des catégories
                                     pour chaque colonne ordinale.
                                     Format: {'nom_col_ord': ['cat1', 'cat2', ...]}

    Returns:
        ColumnTransformer: Objet ColumnTransformer configuré mais non ajusté.

    Raises:
        ValueError: Si les catégories pour une colonne ordinale ne sont pas définies
                    dans `ordinal_categories_map`.
    """
    logger.info("Construction du préprocesseur Sklearn (ColumnTransformer)...")
    transformers_list = []

    if numerical_cols:
        numerical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        transformers_list.append(("num", numerical_transformer, numerical_cols))
        logger.info(f"Transformateur numérique configuré pour les colonnes : {numerical_cols}")

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
        logger.info(f"Transformateur OneHot configuré pour les colonnes : {onehot_cols}")


    if ordinal_cols:
        for col in ordinal_cols:
            if col not in ordinal_categories_map: # Utilisation de ordinal_categories_map
                raise ValueError(
                    f"Les catégories pour la colonne ordinale '{col}' ne sont pas définies dans ordinal_categories_map."
                )
            categories_for_col = [ordinal_categories_map[col]] # Utilisation de ordinal_categories_map
            ordinal_transformer_col = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    (
                        "ordinal",
                        OrdinalEncoder(
                            categories=categories_for_col,
                            handle_unknown="use_encoded_value",
                            unknown_value= np.nan # Utiliser np.nan, qui sera géré par l'imputer numérique si la colonne devient numérique
                                                 # ou -1 si vous préférez et que l'imputer numérique n'est pas appliqué ensuite
                        ),
                    ),
                ]
            )
            transformers_list.append((f"ord_{col}", ordinal_transformer_col, [col]))
        logger.info(f"Transformateurs ordinaux configurés pour les colonnes : {ordinal_cols}")


    if not transformers_list:
        logger.warning("Aucune colonne spécifiée pour le preprocessing. Le ColumnTransformer sera vide et utilisera remainder='passthrough'.")
        # Retourner un transformateur qui ne fait rien mais ne plante pas.
        return ColumnTransformer(transformers=[], remainder="passthrough")

    preprocessor = ColumnTransformer(transformers=transformers_list, remainder="drop")
    logger.info("Préprocesseur Sklearn (ColumnTransformer) construit avec succès.")
    return preprocessor


def run_preprocessing_pipeline(
    df: pd.DataFrame,
    binary_cols_map: dict = None, # Doit venir de config.BINARY_FEATURES_MAPPING
    ordinal_cols_categories_map: dict = None, # Doit venir de config.ORDINAL_FEATURES_CATEGORIES. Renommé pour cohérence.
    preprocessor: ColumnTransformer = None,
    fit: bool = False,
):
    """
    Exécute le pipeline de preprocessing complet sur le DataFrame fourni.

    Orchestre les étapes de nettoyage, mappage binaire, création de features,
    et application (ajustement ou transformation) du ColumnTransformer.

    Args:
        df (pd.DataFrame): DataFrame d'entrée brut.
        binary_cols_map (dict, optional): Mapping pour les features binaires.
                                          Utilise config.BINARY_FEATURES_MAPPING si non fourni (dans l'appelant).
        ordinal_cols_categories_map (dict, optional): Catégories pour les features ordinales.
                                                Utilise config.ORDINAL_FEATURES_CATEGORIES si non fourni (dans l'appelant).
        preprocessor (ColumnTransformer, optional): Un ColumnTransformer pré-ajusté.
                                                  Requis si `fit` est False.
        fit (bool, optional): Si True, le préprocesseur est ajusté (`fit_transform`) sur les données.
                              Si False, le `preprocessor` fourni est utilisé pour transformer (`transform`) les données.
                              Par défaut à False.

    Returns:
        Tuple: Contenant selon le mode `fit`:
               Si `fit` est True: (X_processed_df, y_series, fitted_processor_instance)
               Si `fit` est False: (X_processed_df, y_series)
               Où X_processed_df est un DataFrame et y_series est une Series.

    Raises:
        ValueError: Si la colonne cible est manquante après les premières étapes,
                    ou si `fit` est False et aucun `preprocessor` n'est fourni,
                    ou si une colonne ordinale spécifiée n'existe pas dans le DataFrame.
    """
    logger.info(f"Exécution du pipeline de preprocessing (fit={fit})...")
    df_clean = clean_data(df)

    # Utiliser les mappings passés en argument, ou ceux de config si non fournis par l'appelant
    current_binary_map = binary_cols_map if binary_cols_map is not None else config.BINARY_FEATURES_MAPPING
    if current_binary_map: # Vérifier si le mapping est non vide/None
        df_mapped = map_binary_features(df_clean, current_binary_map)
    else:
        df_mapped = df_clean.copy() # Pas de mappage binaire à faire

    df_featured = create_features(df_mapped)

    if config.TARGET_VARIABLE not in df_featured.columns:
        raise ValueError(
            f"La colonne cible '{config.TARGET_VARIABLE}' n'est pas présente après clean/map/feature."
        )

    y = df_featured[config.TARGET_VARIABLE]
    X = df_featured.drop(config.TARGET_VARIABLE, axis=1)

    # Utiliser les catégories ordinales passées en argument, ou celles de config
    current_ordinal_map = ordinal_cols_categories_map if ordinal_cols_categories_map is not None else config.ORDINAL_FEATURES_CATEGORIES
    ordinal_to_encode = list(current_ordinal_map.keys()) if current_ordinal_map else []


    # Identification des types de colonnes pour le ColumnTransformer
    potential_numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    numerical_to_scale = [
        col for col in potential_numerical_cols if col not in ordinal_to_encode
    ]
    # Les colonnes binaires mappées en 0/1 sont numériques et seront scalées par défaut ici.
    # Si on veut les exclure du scaling, il faudrait les retirer de numerical_to_scale.

    onehot_to_encode = [
        col
        for col in X.select_dtypes(include=["object", "category"]).columns.tolist()
        if col not in ordinal_to_encode
    ]

    # Vérifier que les colonnes ordinales existent bien dans X avant de les passer à build_preprocessor
    for col in ordinal_to_encode:
        if col not in X.columns:
            # Cela peut arriver si une colonne listée dans ORDINAL_FEATURES_CATEGORIES a été droppée
            # ou n'était pas dans le df initial.
            raise ValueError(f"La colonne ordinale '{col}' spécifiée dans ordinal_cols_categories_map n'existe pas dans le DataFrame X.")

    logger.info(f"Colonnes identifiées pour la mise à l'échelle (numériques) : {numerical_to_scale}")
    logger.info(f"Colonnes identifiées pour OneHotEncoding : {onehot_to_encode}")
    logger.info(f"Colonnes identifiées pour OrdinalEncoding : {ordinal_to_encode}")

    if fit:
        # Construire le préprocesseur avec les catégories ordinales actuelles
        processor_instance = build_preprocessor(
            numerical_to_scale,
            onehot_to_encode,
            ordinal_to_encode,
            current_ordinal_map, # Passer le dictionnaire complet
        )
        logger.info("Ajustement (fit) et transformation des données X...")
        X_processed = processor_instance.fit_transform(X)
        try:
            feature_names = processor_instance.get_feature_names_out()
        except Exception as e:
            logger.warning(
                f"Impossible d'obtenir les noms de features via get_feature_names_out(): {e}. Noms génériques utilisés."
            )
            feature_names = [f"feature_{i}" for i in range(X_processed.shape[1])]
        logger.info("Transformation X terminée.")
        return (
            pd.DataFrame(X_processed, columns=feature_names, index=X.index),
            y,
            processor_instance,
        )
    else: # Mode transform uniquement
        if preprocessor:
            logger.info("Transformation des données X (sans ajustement) en utilisant le préprocesseur fourni...")
            X_processed = preprocessor.transform(X)
            try:
                feature_names = preprocessor.get_feature_names_out()
            except Exception as e:
                logger.warning(
                    f"Impossible d'obtenir les noms de features via get_feature_names_out(): {e}. Noms génériques utilisés."
                )
                feature_names = [f"feature_{i}" for i in range(X_processed.shape[1])]
            logger.info("Transformation X terminée.")
            return pd.DataFrame(X_processed, columns=feature_names, index=X.index), y
        else:
            logger.error("Erreur: `fit` est False mais aucun `preprocessor` n'a été fourni.")
            raise ValueError("Un preprocessor doit être fourni si fit=False.")


# Bloc de test pour une exécution directe (poetry run python -m src.data_processing.preprocess)
if __name__ == "__main__":
    logger.info("--- Démarrage du test direct du module preprocess.py ---")
    # Importer load_and_merge_csvs ici pour éviter l'import circulaire au niveau du module
    # si load_data devait importer qqch de preprocess (ce qui n'est pas le cas actuellement)
    try:
        from src.data_processing.load_data import load_and_merge_csvs
        df_raw = load_and_merge_csvs()

        if df_raw is not None and not df_raw.empty:
            logger.info(f"Données brutes chargées pour le test: {df_raw.shape[0]} lignes.")
            # Test du pipeline de preprocessing complet en mode fit=True
            # Les mappings et catégories sont pris depuis config.py par défaut dans run_preprocessing_pipeline
            X_p, y_p, proc = run_preprocessing_pipeline(
                df_raw,
                # binary_cols_map et ordinal_cols_categories sont pris de config par défaut
                fit=True,
            )
            print("\n--- Preprocessing Réussi (fit=True) ---")
            print("Shape X_processed:", X_p.shape)
            print("X_processed (head):")
            print(X_p.head())
            print("\ny (head):")
            print(y_p.head())
            print("\nColonnes après preprocessing:", X_p.columns.tolist())

            # Exemple de test en mode transform=True avec le processeur fitté
            # On prend un échantillon des données brutes pour simuler de nouvelles données
            if len(df_raw) > 5:
                df_sample_for_transform = df_raw.sample(n=min(5, len(df_raw)), random_state=42)
                logger.info(f"\nTest du mode transform sur {len(df_sample_for_transform)} échantillons...")
                X_t, y_t = run_preprocessing_pipeline(
                    df_sample_for_transform,
                    preprocessor=proc, # Utiliser le processeur fitté
                    fit=False
                )
                print("\n--- Preprocessing Réussi (fit=False) ---")
                print("Shape X_transformed:", X_t.shape)
                print("X_transformed (head):")
                print(X_t.head())
        else:
            logger.error("Impossible de charger les données brutes pour le test du module preprocess.")

    except Exception as e_main:
        print(f"\n--- Erreur lors de l'exécution du test de preprocess.py ---")
        print(e_main)
        import traceback
        traceback.print_exc()
    logger.info("--- Fin du test direct du module preprocess.py ---")