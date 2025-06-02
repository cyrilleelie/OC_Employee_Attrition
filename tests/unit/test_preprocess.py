import pandas as pd
import pytest  # pytest est implicitement utilisé mais l'import est une bonne pratique
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer
from src.data_processing.preprocess import (
    map_binary_features,
    clean_data,
    build_preprocessor,
    run_preprocessing_pipeline,
)
from src import config  # Pour config.TARGET_VARIABLE


# --- Tests existants pour map_binary_features (assurez-vous qu'ils sont robustes) ---
def test_map_binary_features_simple_case():
    """Teste le mappage binaire simple."""
    data = {"genre": ["M", "F", "M"]}
    df_input = pd.DataFrame(data)
    binary_map = {"genre": {"M": 0, "F": 1}}
    df_expected_data = {"genre": [0, 1, 0]}
    df_expected = pd.DataFrame(df_expected_data)
    df_output = map_binary_features(df_input, binary_map)
    pd.testing.assert_frame_equal(
        df_output, df_expected, check_dtype=False
    )  # check_dtype=False peut être utile


def test_map_binary_features_missing_column():
    """Teste le comportement si une colonne à mapper est absente."""
    data = {"autre_col": ["A", "B"]}
    df_input = pd.DataFrame(data)
    binary_map = {"genre": {"M": 0, "F": 1}}
    df_output = map_binary_features(df_input, binary_map)
    pd.testing.assert_frame_equal(df_output, df_input)


def test_map_binary_features_unmapped_values():
    """Teste le comportement avec des valeurs non présentes dans le mapping."""
    data = {"genre": ["M", "F", "Autre"]}
    df_input = pd.DataFrame(data)
    binary_map = {"genre": {"M": 0, "F": 1}}
    df_output = map_binary_features(df_input, binary_map)
    assert df_output["genre"].iloc[0] == 0
    assert df_output["genre"].iloc[1] == 1
    assert pd.isna(df_output["genre"].iloc[2])  # Les valeurs non mappées deviennent NaN


@pytest.fixture
def sample_df_for_clean():
    """Crée un DataFrame d'exemple pour tester clean_data."""
    data = {
        "employee_id": [1, 2, 3, 4],
        "a_quitte_l_entreprise": ["Oui", "Non", "Oui", "Non"],
        "eval_number": ["E_1", "E_2", "E_3", "E_4"],
        "augementation_salaire_precedente": [
            "10 %",
            "5 %",
            "12 %",
            "Pas d'augmentation",
        ],  # Ajout d'un cas problématique
        "feature_a_garder": [100, 200, 150, 250],
    }
    return pd.DataFrame(data)


def test_clean_data_target_conversion(sample_df_for_clean):
    """Vérifie la conversion correcte de la variable cible."""
    df_cleaned = clean_data(sample_df_for_clean)
    assert config.TARGET_VARIABLE in df_cleaned.columns
    expected_series = pd.Series([1, 0, 1, 0], name=config.TARGET_VARIABLE, dtype='Int64') # Spécifier dtype
    assert df_cleaned[config.TARGET_VARIABLE].equals(expected_series)


def test_clean_data_column_dropping(sample_df_for_clean):
    """Vérifie la suppression des colonnes spécifiées."""
    df_cleaned = clean_data(sample_df_for_clean)
    assert "eval_number" not in df_cleaned.columns
    assert "id_employee" not in df_cleaned.columns
    assert "a_quitte_l_entreprise" not in df_cleaned.columns  # La version texte
    assert "feature_a_garder" in df_cleaned.columns


def test_clean_data_percentage_conversion(sample_df_for_clean):
    """Vérifie la conversion de la colonne de pourcentage en numérique."""
    col_aug = "augementation_salaire_precedente"
    df_cleaned = clean_data(sample_df_for_clean)

    assert col_aug in df_cleaned.columns
    assert df_cleaned[col_aug].dtype == "float64"  # Devrait être float après to_numeric
    assert df_cleaned[col_aug].iloc[0] == 10.0
    assert df_cleaned[col_aug].iloc[1] == 5.0
    assert df_cleaned[col_aug].iloc[2] == 12.0
    assert pd.isna(
        df_cleaned[col_aug].iloc[3]
    )  # "Pas d'augmentation" devient NaN à cause de errors='coerce'


def test_build_preprocessor_all_types():
    """Teste build_preprocessor avec tous les types de colonnes."""
    numerical_cols = ["age", "salaire"]
    onehot_cols = ["departement", "poste"]
    ordinal_cols = ["frequence_deplacement"]
    ordinal_categories = {"frequence_deplacement": ["Bas", "Moyen", "Haut"]}

    preprocessor = build_preprocessor(
        numerical_cols, onehot_cols, ordinal_cols, ordinal_categories
    )

    assert isinstance(preprocessor, ColumnTransformer)
    assert (
        len(preprocessor.transformers) == 3
    )  # Un pour num, un pour onehot, un pour ord_frequence_deplacement

    # Vérifier le transformateur numérique
    num_transformer_tuple = next(t for t in preprocessor.transformers if t[0] == "num")
    assert isinstance(num_transformer_tuple[1], Pipeline)
    assert len(num_transformer_tuple[1].steps) == 2
    assert isinstance(num_transformer_tuple[1].steps[0][1], SimpleImputer)
    assert num_transformer_tuple[1].steps[0][1].strategy == "median"
    assert isinstance(num_transformer_tuple[1].steps[1][1], StandardScaler)
    assert num_transformer_tuple[2] == numerical_cols

    # Vérifier le transformateur one-hot
    onehot_transformer_tuple = next(
        t for t in preprocessor.transformers if t[0] == "onehot"
    )
    assert isinstance(onehot_transformer_tuple[1], Pipeline)
    assert len(onehot_transformer_tuple[1].steps) == 2
    assert isinstance(onehot_transformer_tuple[1].steps[0][1], SimpleImputer)
    assert onehot_transformer_tuple[1].steps[0][1].strategy == "most_frequent"
    assert isinstance(onehot_transformer_tuple[1].steps[1][1], OneHotEncoder)
    assert onehot_transformer_tuple[1].steps[1][1].drop == "first"
    assert onehot_transformer_tuple[1].steps[1][1].handle_unknown == "ignore"
    assert onehot_transformer_tuple[2] == onehot_cols

    # Vérifier le transformateur ordinal pour 'frequence_deplacement'
    ord_transformer_tuple = next(
        t for t in preprocessor.transformers if t[0] == "ord_frequence_deplacement"
    )
    assert isinstance(ord_transformer_tuple[1], Pipeline)
    assert len(ord_transformer_tuple[1].steps) == 2
    assert isinstance(ord_transformer_tuple[1].steps[0][1], SimpleImputer)
    assert isinstance(ord_transformer_tuple[1].steps[1][1], OrdinalEncoder)
    assert ord_transformer_tuple[1].steps[1][1].categories == [["Bas", "Moyen", "Haut"]]
    assert ord_transformer_tuple[2] == ["frequence_deplacement"]


def test_build_preprocessor_only_numerical():
    """Teste build_preprocessor avec seulement des colonnes numériques."""
    numerical_cols = ["age", "salaire"]
    preprocessor = build_preprocessor(numerical_cols, [], [], {})
    assert isinstance(preprocessor, ColumnTransformer)
    assert len(preprocessor.transformers) == 1
    assert preprocessor.transformers[0][0] == "num"
    assert preprocessor.transformers[0][2] == numerical_cols


def test_build_preprocessor_ordinal_col_missing_categories():
    """Teste que build_preprocessor lève une erreur si une catégorie ordinale est manquante."""
    numerical_cols = []
    onehot_cols = []
    ordinal_cols = [
        "niveau_satisfaction"
    ]  # Cette colonne n'est pas dans ordinal_categories
    expected_error_message = "Les catégories pour la colonne ordinale 'niveau_satisfaction' ne sont pas définies dans ordinal_categories_map."
    with pytest.raises(ValueError, match=expected_error_message):
        build_preprocessor(numerical_cols, onehot_cols, ordinal_cols, config.ORDINAL_FEATURES_CATEGORIES) # Utilisez un nom de variable clair pour le dict de catégories


def test_build_preprocessor_no_cols():
    """Teste build_preprocessor quand aucune colonne n'est spécifiée."""
    preprocessor = build_preprocessor([], [], [], {})
    assert isinstance(preprocessor, ColumnTransformer)
    assert (
        len(preprocessor.transformers) == 0
    )  # Devrait retourner un ColumnTransformer vide
    assert (
        preprocessor.remainder == "passthrough"
    )  # Selon votre implémentation actuelle
    # (j'avais mis 'drop', si c'est passthrough, adaptez le test ou la fonction)
    # Ma version de build_preprocessor avait 'remainder="drop"' et retournait un CT vide.
    # Si vous voulez qu'il soit 'passthrough' dans ce cas, modifiez la fonction ou le test.
    # Pour 'remainder="drop"', len(preprocessor.transformers) == 0 est correct.


@pytest.fixture
def sample_raw_df_for_pipeline():
    """DataFrame brut d'exemple pour tester le pipeline complet."""
    data = {
        "employee_id": ["E_1", "E_2", "E_3", "E_4"],
        "a_quitte_l_entreprise": ["Oui", "Non", "Oui", "Non"],
        "genre": ["M", "F", "M", "F"],
        "heure_supplementaires": ["Oui", "Non", "Non", "Oui"],
        "frequence_deplacement": ["Occasionnel", "Aucun", "Frequent", "Occasionnel"],
        "augmentation_salaire_precedente": ["10 %", "5 %", "12 %", "8 %"],
        "age": [30, 45, 22, 50],
        "salaire_mensuel_brut": [5000, 8000, 3500, 9000],
        "departement": ["Ventes", "R&D", "Ventes", "Marketing"],
        # Ajoutez d'autres colonnes pour couvrir tous vos types
        config.TARGET_VARIABLE: [
            1,
            0,
            1,
            0,
        ],  # La fonction clean_data va écraser ça, mais pour la cohérence
    }
    return pd.DataFrame(data)


def test_run_preprocessing_pipeline_fit_true(sample_raw_df_for_pipeline):
    """Teste run_preprocessing_pipeline en mode fit=True."""
    df_in = sample_raw_df_for_pipeline.copy()

    X_processed, y_processed, fitted_processor = run_preprocessing_pipeline(
        df_in,
        binary_cols_map=config.BINARY_FEATURES_MAPPING,
        ordinal_cols_categories_map=config.ORDINAL_FEATURES_CATEGORIES,
        fit=True,
    )

    assert isinstance(X_processed, pd.DataFrame)
    assert isinstance(y_processed, pd.Series)
    assert isinstance(fitted_processor, ColumnTransformer)
    assert X_processed.shape[0] == len(df_in)
    assert y_processed.shape[0] == len(df_in)

    # Vérifier que les colonnes attendues (après OHE, etc.) sont là
    # Ceci dépendra de vos colonnes exactes et de get_feature_names_out
    # Par exemple, on s'attend à voir des colonnes issues du OHE de 'departement'
    assert any(col.startswith("onehot__departement_") for col in X_processed.columns)
    assert "num__age" in X_processed.columns
    assert (
        f'ord_frequence_deplacement__{config.ORDINAL_FEATURES_CATEGORIES["frequence_deplacement"][0]}'
        not in X_processed.columns
    )  # OrdinalEncoder ne préfixe pas comme ça
    assert (
        "ord_frequence_deplacement__frequence_deplacement" in X_processed.columns
    )  # ou juste 'frequence_deplacement' si remainder='passthrough' et ord pas dans CT

    # Vérifier que le processeur est "fitté" (ex: StandardScaler a mean_ et scale_)
    # Accéder au transformateur numérique dans le ColumnTransformer
    num_pipeline = fitted_processor.named_transformers_["num"]
    scaler = num_pipeline.named_steps["scaler"]
    assert hasattr(scaler, "mean_") and scaler.mean_ is not None


@pytest.mark.filterwarnings("ignore:Found unknown categories.*:UserWarning")
def test_run_preprocessing_pipeline_fit_false(sample_raw_df_for_pipeline):
    """Teste run_preprocessing_pipeline en mode fit=False (transform)."""
    df_train = sample_raw_df_for_pipeline.sample(frac=0.5, random_state=42)
    df_test = sample_raw_df_for_pipeline.drop(df_train.index)

    _, _, fitted_processor = run_preprocessing_pipeline(
        df_train,
        binary_cols_map=config.BINARY_FEATURES_MAPPING,
        ordinal_cols_categories_map=config.ORDINAL_FEATURES_CATEGORIES,
        fit=True,
    )

    X_test_processed, y_test_processed = run_preprocessing_pipeline(
        df_test,
        binary_cols_map=config.BINARY_FEATURES_MAPPING,  # Toujours nécessaire pour map_binary_features
        ordinal_cols_categories_map=config.ORDINAL_FEATURES_CATEGORIES,  # Toujours nécessaire pour build_preprocessor si pas fitté
        preprocessor=fitted_processor,
        fit=False,
    )

    assert isinstance(X_test_processed, pd.DataFrame)
    assert X_test_processed.shape[0] == len(df_test)
    # Le nombre de colonnes doit être le même que celui obtenu après fit_transform sur le train
    # Pour cela, il faudrait stocker X_train_processed.shape[1] du test précédent


def test_run_preprocessing_pipeline_fit_false_no_processor(sample_raw_df_for_pipeline): # Utilisez la fixture
    """Teste que fit=False sans preprocessor lève une ValueError pour cette raison spécifique."""
    # Utilisez un DataFrame d'entrée qui est suffisamment complet pour passer les étapes
    # de clean_data, map_binary_features, create_features et l'identification des colonnes.
    # La fixture sample_raw_df_for_pipeline devrait convenir si elle est bien définie.
    df_in = sample_raw_df_for_pipeline.copy() 

    with pytest.raises(
        ValueError, match="Un preprocessor doit être fourni si fit=False."
    ):
        # Appelez avec les mappings pour éviter des erreurs avant le check final
        run_preprocessing_pipeline(
            df_in,
            binary_cols_map=config.BINARY_FEATURES_MAPPING,
            ordinal_cols_categories_map=config.ORDINAL_FEATURES_CATEGORIES,
            preprocessor=None, # Explicitement None
            fit=False
        )
