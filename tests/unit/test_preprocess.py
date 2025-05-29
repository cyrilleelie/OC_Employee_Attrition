import pandas as pd
import pytest # pytest est implicitement utilisé mais l'import est une bonne pratique
import numpy as np # Pour pd.NA et les types numériques

# Importez les fonctions que vous voulez tester
from src.data_processing.preprocess import map_binary_features, clean_data
from src import config # Pour config.TARGET_VARIABLE

# --- Tests existants pour map_binary_features (assurez-vous qu'ils sont robustes) ---
def test_map_binary_features_simple_case():
    """Teste le mappage binaire simple."""
    data = {'genre': ['M', 'F', 'M']}
    df_input = pd.DataFrame(data)
    binary_map = {'genre': {'M': 0, 'F': 1}}
    df_expected_data = {'genre': [0, 1, 0]}
    df_expected = pd.DataFrame(df_expected_data)
    df_output = map_binary_features(df_input, binary_map)
    pd.testing.assert_frame_equal(df_output, df_expected, check_dtype=False) # check_dtype=False peut être utile

def test_map_binary_features_missing_column():
    """Teste le comportement si une colonne à mapper est absente."""
    data = {'autre_col': ['A', 'B']}
    df_input = pd.DataFrame(data)
    binary_map = {'genre': {'M': 0, 'F': 1}}
    df_output = map_binary_features(df_input, binary_map)
    pd.testing.assert_frame_equal(df_output, df_input)

def test_map_binary_features_unmapped_values():
    """Teste le comportement avec des valeurs non présentes dans le mapping."""
    data = {'genre': ['M', 'F', 'Autre']}
    df_input = pd.DataFrame(data)
    binary_map = {'genre': {'M': 0, 'F': 1}}
    df_output = map_binary_features(df_input, binary_map)
    assert df_output['genre'].iloc[0] == 0
    assert df_output['genre'].iloc[1] == 1
    assert pd.isna(df_output['genre'].iloc[2]) # Les valeurs non mappées deviennent NaN

# --- Nouveaux Tests pour clean_data ---
@pytest.fixture
def sample_df_for_clean():
    """Crée un DataFrame d'exemple pour tester clean_data."""
    data = {
        'employee_id': [1, 2, 3, 4],
        'a_quitte_l_entreprise': ['Oui', 'Non', 'Oui', 'Non'],
        'eval_number': ['E_1', 'E_2', 'E_3', 'E_4'],
        'augementation_salaire_precedente': ["10 %", "5 %", "12 %", "Pas d'augmentation"], # Ajout d'un cas problématique
        'feature_a_garder': [100, 200, 150, 250]
    }
    return pd.DataFrame(data)

def test_clean_data_target_conversion(sample_df_for_clean):
    """Vérifie la conversion correcte de la variable cible."""
    df_cleaned = clean_data(sample_df_for_clean)
    assert config.TARGET_VARIABLE in df_cleaned.columns
    assert df_cleaned[config.TARGET_VARIABLE].equals(pd.Series([1, 0, 1, 0], name=config.TARGET_VARIABLE))

def test_clean_data_column_dropping(sample_df_for_clean):
    """Vérifie la suppression des colonnes spécifiées."""
    df_cleaned = clean_data(sample_df_for_clean)
    assert 'eval_number' not in df_cleaned.columns
    assert 'id_employee' not in df_cleaned.columns
    assert 'a_quitte_l_entreprise' not in df_cleaned.columns # La version texte
    assert 'feature_a_garder' in df_cleaned.columns

def test_clean_data_percentage_conversion(sample_df_for_clean):
    """Vérifie la conversion de la colonne de pourcentage en numérique."""
    col_aug = 'augementation_salaire_precedente'
    df_cleaned = clean_data(sample_df_for_clean)
    
    assert col_aug in df_cleaned.columns
    assert df_cleaned[col_aug].dtype == 'float64' # Devrait être float après to_numeric
    assert df_cleaned[col_aug].iloc[0] == 10.0
    assert df_cleaned[col_aug].iloc[1] == 5.0
    assert df_cleaned[col_aug].iloc[2] == 12.0
    assert pd.isna(df_cleaned[col_aug].iloc[3]) # "Pas d'augmentation" devient NaN à cause de errors='coerce'

def test_clean_data_with_missing_target_column():
    """Vérifie que clean_data lève une erreur si la colonne cible est manquante."""
    data = {'employee_id': [1], 'eval_number': ['E_1']}
    df_no_target = pd.DataFrame(data)
    with pytest.raises(ValueError, match="Colonne cible manquante"):
        clean_data(df_no_target)