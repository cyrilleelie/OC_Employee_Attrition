import pandas as pd
import pytest # Import facultatif si vous n'utilisez pas de fixtures pytest spécifiques ici

# Importez la fonction que vous voulez tester
# Attention au chemin d'import relatif à la racine du projet
from src.data_processing.preprocess import map_binary_features

def test_map_binary_features_simple_case():
    """Teste le mappage binaire simple."""
    data = {'genre': ['M', 'F', 'M']}
    df_input = pd.DataFrame(data)

    binary_map = {'genre': {'M': 0, 'F': 1}}

    df_expected_data = {'genre': [0, 1, 0]}
    df_expected = pd.DataFrame(df_expected_data)

    df_output = map_binary_features(df_input, binary_map)

    pd.testing.assert_frame_equal(df_output, df_expected)

def test_map_binary_features_missing_column():
    """Teste le comportement si une colonne à mapper est absente."""
    data = {'autre_col': ['A', 'B']}
    df_input = pd.DataFrame(data)

    binary_map = {'genre': {'M': 0, 'F': 1}} # 'genre' n'est pas dans df_input

    # On s'attend à ce que la fonction retourne le DataFrame inchangé
    # car elle logue un warning mais ne doit pas planter.
    df_output = map_binary_features(df_input, binary_map)

    pd.testing.assert_frame_equal(df_output, df_input)

def test_map_binary_features_unmapped_values():
    """Teste le comportement avec des valeurs non présentes dans le mapping."""
    data = {'genre': ['M', 'F', 'Autre']} # 'Autre' n'est pas dans le mapping
    df_input = pd.DataFrame(data)

    binary_map = {'genre': {'M': 0, 'F': 1}}

    df_output = map_binary_features(df_input, binary_map)

    # Les valeurs non mappées deviennent NaN avec .map()
    # Notre fonction map_binary_features devrait gérer cela (ou nous devrions le spécifier)
    # Dans la version actuelle, elle devrait introduire des NaN.
    assert df_output['genre'].iloc[0] == 0
    assert df_output['genre'].iloc[1] == 1
    assert pd.isna(df_output['genre'].iloc[2])