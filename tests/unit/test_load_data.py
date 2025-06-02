import pandas as pd
from unittest.mock import patch, MagicMock, call

from src.data_processing.load_data import (
    load_data_from_csv,
    load_data_from_postgres,
    get_data,
    load_and_merge_csvs,
)
from src import config as app_config  # Pour config.PROCESSED_DATA_PATH

# Supposons que Employee est défini dans models.py pour le test de load_data_from_postgres
# from src.database.models import Employee # Nécessaire si on mock db.query(Employee) spécifiquement


@patch("src.data_processing.load_data.pd.read_csv")
@patch("src.data_processing.load_data.logger")
def test_load_data_from_csv_success(mock_logger, mock_read_csv):
    """Teste le chargement réussi depuis un CSV."""
    sample_df = pd.DataFrame({"col1": [1], "col2": ["a"]})
    mock_read_csv.return_value = sample_df

    dummy_path = "dummy_path.csv"
    df = load_data_from_csv(dummy_path)  # path est dummy_path

    mock_read_csv.assert_called_once_with(dummy_path)
    mock_logger.info.assert_any_call(
        f"Chargement des données CSV depuis {dummy_path}..."
    )
    mock_logger.info.assert_any_call(
        f"Données CSV chargées avec succès depuis {dummy_path}: {len(sample_df)} lignes."
    )
    pd.testing.assert_frame_equal(df, sample_df)


@patch("src.data_processing.load_data.pd.read_csv")
@patch("src.data_processing.load_data.logger")
def test_load_data_from_csv_file_not_found(mock_logger, mock_read_csv):
    """Teste la gestion de FileNotFoundError pour load_data_from_csv."""
    mock_read_csv.side_effect = FileNotFoundError("File not found")

    df = load_data_from_csv("non_existent.csv")

    assert df is None
    mock_logger.error.assert_called_once_with(
        "Fichier CSV non trouvé : non_existent.csv"
    )


@patch("src.data_processing.load_data.SessionLocal")  # Mocker la classe SessionLocal
@patch("src.data_processing.load_data.pd.read_sql_query")
@patch("src.data_processing.load_data.logger")
def test_load_data_from_postgres_success(mock_logger, mock_read_sql, mock_SessionLocal):
    """Teste le chargement réussi depuis PostgreSQL."""
    sample_df = pd.DataFrame({"id_employee": ["E_1"], "age": [30]})
    mock_read_sql.return_value = sample_df

    # Configurer le mock de la session et de la query
    mock_db_session = MagicMock()
    mock_SessionLocal.return_value = (
        mock_db_session  # Quand SessionLocal() est appelé, il retourne notre mock
    )

    # Si votre query est db.query(Employee), vous pouvez mocker Employee
    # from src.database.models import Employee (déjà importé si décommenté plus haut)
    # mock_query_obj = MagicMock()
    # mock_db_session.query.return_value = mock_query_obj

    df = load_data_from_postgres()

    mock_SessionLocal.assert_called_once()  # Vérifie que SessionLocal() a été instancié
    # mock_db_session.query.assert_called_once_with(Employee) # Si vous mockez Employee
    # mock_read_sql.assert_called_once_with(mock_query_obj.statement, mock_db_session.bind)
    # Version plus simple si on ne mocke pas la query en détail :
    assert mock_read_sql.call_count == 1

    mock_logger.info.assert_any_call(
        "Chargement des données depuis la table 'employees' de PostgreSQL..."
    )
    mock_logger.info.assert_any_call(
        f"{len(sample_df)} lignes chargées depuis la table 'employees'."
    )
    pd.testing.assert_frame_equal(df, sample_df)
    mock_db_session.close.assert_called_once()  # Vérifie que la session est fermée


@patch("src.data_processing.load_data.SessionLocal")
@patch("src.data_processing.load_data.pd.read_sql_query")
@patch("src.data_processing.load_data.logger")
def test_load_data_from_postgres_empty(mock_logger, mock_read_sql, mock_SessionLocal):
    """Teste le chargement depuis PostgreSQL quand la table est vide."""
    empty_df = pd.DataFrame()
    mock_read_sql.return_value = empty_df
    mock_db_session = MagicMock()
    mock_SessionLocal.return_value = mock_db_session

    df = load_data_from_postgres()

    pd.testing.assert_frame_equal(df, empty_df)
    mock_logger.warning.assert_called_once_with(
        "Aucune donnée trouvée dans la table 'employees'. Le DataFrame est vide."
    )
    mock_db_session.close.assert_called_once()


@patch("src.data_processing.load_data.SessionLocal")
@patch("src.data_processing.load_data.pd.read_sql_query")
@patch("src.data_processing.load_data.logger")
def test_load_data_from_postgres_exception(
    mock_logger, mock_read_sql, mock_SessionLocal
):
    """Teste la gestion d'exception lors du chargement depuis PostgreSQL."""
    mock_read_sql.side_effect = Exception("DB Connection Error")
    mock_db_session = MagicMock()
    mock_SessionLocal.return_value = mock_db_session

    df = load_data_from_postgres()

    assert df.empty  # Doit retourner un DataFrame vide
    mock_logger.error.assert_called_once_with(
        "Erreur lors du chargement des données depuis PostgreSQL : DB Connection Error",
        exc_info=True,
    )
    mock_db_session.close.assert_called_once()


@patch("src.data_processing.load_data.load_data_from_postgres")
@patch(
    "src.data_processing.load_data.load_and_merge_csvs"
)  # Si get_data(source='csv') l'appelle
# Ou @patch('src.data_processing.load_data.load_data_from_csv') si c'est ce qu'elle appelle
def test_get_data_source_postgres(mock_load_csv_or_merge, mock_load_postgres):
    """Teste get_data avec source='postgres'."""
    mock_load_postgres.return_value = "data_from_db"
    result = get_data(source="postgres")
    mock_load_postgres.assert_called_once()
    mock_load_csv_or_merge.assert_not_called()
    assert result == "data_from_db"


@patch("src.data_processing.load_data.load_data_from_postgres")
@patch("src.data_processing.load_data.load_and_merge_csvs")  # Adaptez ce mock
def test_get_data_source_csv(mock_load_csv_or_merge, mock_load_postgres):
    """Teste get_data avec source='csv'."""
    mock_load_csv_or_merge.return_value = "data_from_csv"
    result = get_data(source="csv")
    mock_load_csv_or_merge.assert_called_once()
    mock_load_postgres.assert_not_called()
    assert result == "data_from_csv"


@patch("src.data_processing.load_data.load_data_from_postgres")
@patch("src.data_processing.load_data.logger")
def test_get_data_invalid_source(mock_logger, mock_load_postgres):
    """Teste get_data avec une source invalide (doit utiliser postgres par défaut)."""
    mock_load_postgres.return_value = "data_from_db_default"
    result = get_data(source="invalid_source")
    mock_load_postgres.assert_called_once()  # Appelée car c'est le défaut
    source_name = "invalid_source"
    expected_log_msg = f"Source de données non reconnue : {source_name}. Tentative avec PostgreSQL par défaut."
    mock_logger.error.assert_any_call(expected_log_msg)
    assert result == "data_from_db_default"


@patch(
    "src.data_processing.load_data.logger"
)  # Mocker le logger en premier (ordre des décorateurs inversé)
@patch("src.data_processing.load_data.pd.read_csv")
def test_load_and_merge_csvs_success(mock_read_csv, mock_logger):
    """Teste le chargement et la fusion réussis des 3 CSV."""
    # 1. Préparer les DataFrames de simulation retournés par read_csv
    df_sirh_sample = pd.DataFrame(
        {"id_employee": ["1", "2", "3"], "sirh_feature": ["A1", "A2", "A3"]}
    )
    # df_eval avec des eval_number qui seront transformés en id_employee '1', '2', 'SPECIAL'
    df_eval_sample = pd.DataFrame(
        {
            "eval_number": ["E_1", "E_2", "E_SPECIAL"],
            "eval_feature": ["EvalX", "EvalY", "EvalZ"],
        }
    )
    df_sondage_sample = pd.DataFrame(
        {
            "id_employee": ["1", "3"],  # ID '2' manquant, 'SPECIAL' non présent
            "sondage_feature": ["SondA", "SondC"],
        }
    )

    # Configurer le side_effect de mock_read_csv pour retourner ces DataFrames dans l'ordre
    mock_read_csv.side_effect = [df_sirh_sample, df_eval_sample, df_sondage_sample]

    # 2. Appeler la fonction à tester
    merged_df = load_and_merge_csvs()

    # 3. Vérifications
    # Vérifier les appels à pd.read_csv avec les bons chemins
    expected_calls = [
        call(app_config.RAW_SIRH_PATH),
        call(app_config.RAW_EVAL_PATH),
        call(app_config.RAW_SONDAGE_PATH),
    ]
    mock_read_csv.assert_has_calls(expected_calls, any_order=False)
    assert mock_read_csv.call_count == 3

    # Vérifier les logs importants
    mock_logger.info.assert_any_call("Chargement des fichiers CSV bruts pour fusion...")
    mock_logger.info.assert_any_call(
        "Préparation de la clé de jointure 'id_employee' dans df_eval à partir de 'eval_number'..."
    )
    mock_logger.info.assert_any_call(
        "Préparation de la clé de jointure 'id_employee' dans df_sondage à partir de 'code_sondage'..."
    )
    # mock_logger.info.assert_any_call("'id_employee' créé dans df_eval.") # log absent du fichier load_data.py
    mock_logger.info.assert_any_call(
        "Fusion des DataFrames (df_sirh <- df_eval <- df_sondage)..."
    )
    # mock_logger.info.assert_any_call(f"Données fusionnées : {merged_df.shape}") # Le shape peut varier

    # Vérifier le DataFrame fusionné
    assert merged_df is not None
    assert list(merged_df.columns) == [
        "id_employee",
        "sirh_feature",
        "eval_number",
        "eval_feature",
        "sondage_feature",
    ]
    assert len(merged_df) == 3  # Car left merge depuis df_sirh_sample

    # Vérifier le contenu (basé sur df_sirh en tant que table de gauche pour les merges)
    # Ligne pour id_employee '1'
    row_1 = merged_df[merged_df["id_employee"] == "1"].iloc[0]
    assert row_1["sirh_feature"] == "A1"
    assert row_1["eval_feature"] == "EvalX"
    assert row_1["sondage_feature"] == "SondA"

    # Ligne pour id_employee '2'
    row_2 = merged_df[merged_df["id_employee"] == "2"].iloc[0]
    assert row_2["sirh_feature"] == "A2"
    assert row_2["eval_feature"] == "EvalY"
    assert pd.isna(row_2["sondage_feature"])  # Pas de '2' dans df_sondage_sample

    # Ligne pour id_employee '3'
    row_3 = merged_df[merged_df["id_employee"] == "3"].iloc[0]
    assert row_3["sirh_feature"] == "A3"
    assert pd.isna(
        row_3["eval_feature"]
    )  # 'E_3' n'est pas dans df_eval_sample, df_eval a 'E_SPECIAL' qui donne 'SPECIAL'
    assert row_3["sondage_feature"] == "SondC"

    # Vérifier le type de la colonne 'id_employee'
    assert merged_df["id_employee"].dtype == "object"


@patch("src.data_processing.load_data.logger")
@patch("src.data_processing.load_data.pd.read_csv")
def test_load_and_merge_csvs_sirh_file_not_found(mock_read_csv, mock_logger):
    """Teste FileNotFoundError pour le fichier SIRH."""
    mock_read_csv.side_effect = FileNotFoundError("SIRH file missing")

    result_df = load_and_merge_csvs()

    assert result_df is None
    mock_logger.error.assert_any_call(
        "Erreur de chargement CSV : Fichier non trouvé - SIRH file missing"
    )


@patch("src.data_processing.load_data.logger")
@patch("src.data_processing.load_data.pd.read_csv")
def test_load_and_merge_csvs_eval_file_not_found(mock_read_csv, mock_logger):
    """Teste FileNotFoundError pour le fichier EVAL."""
    df_sirh_sample = pd.DataFrame({"id_employee": ["1"]})
    mock_read_csv.side_effect = [df_sirh_sample, FileNotFoundError("EVAL file missing")]

    result_df = load_and_merge_csvs()

    assert result_df is None
    mock_logger.error.assert_any_call(
        "Erreur de chargement CSV : Fichier non trouvé - EVAL file missing"
    )


@patch("src.data_processing.load_data.logger")
@patch("src.data_processing.load_data.pd.read_csv")
def test_load_and_merge_csvs_missing_eval_number_col(mock_read_csv, mock_logger):
    """Teste le cas où 'eval_number' manque dans df_eval."""
    df_sirh_sample = pd.DataFrame({"id_employee": ["1"]})
    df_eval_no_eval_number = pd.DataFrame({"autre_col": ["X"]})  # Pas de eval_number
    df_sondage_sample = pd.DataFrame({"id_employee": ["1"]})
    mock_read_csv.side_effect = [
        df_sirh_sample,
        df_eval_no_eval_number,
        df_sondage_sample,
    ]

    result_df = load_and_merge_csvs()

    assert result_df is None
    mock_logger.error.assert_any_call(
        "La colonne 'eval_number' est introuvable dans df_eval. Impossible de créer 'id_employee'."
    )


@patch("src.data_processing.load_data.logger")
@patch("src.data_processing.load_data.pd.read_csv")
def test_load_and_merge_csvs_missing_id_employee_in_sirh(mock_read_csv, mock_logger):
    """Teste le cas où 'id_employee' manque dans df_sirh."""
    df_sirh_no_id = pd.DataFrame({"autre_col_sirh": ["Y"]})  # Pas de id_employee
    df_eval_sample = pd.DataFrame({"eval_number": ["E_1"]})
    df_sondage_sample = pd.DataFrame({"id_employee": ["1"]})
    mock_read_csv.side_effect = [df_sirh_no_id, df_eval_sample, df_sondage_sample]

    result_df = load_and_merge_csvs()

    assert result_df is None
    mock_logger.error.assert_any_call(
        "La colonne 'id_employee' est introuvable dans df_sirh."
    )


@patch("src.data_processing.load_data.logger")
@patch("src.data_processing.load_data.pd.read_csv")
def test_load_and_merge_csvs_eval_number_conversion_warning(mock_read_csv, mock_logger):
    """Teste le warning pour les eval_number non convertibles."""
    df_sirh_sample = pd.DataFrame({"id_employee": ["1", "bad_id_format"]})
    df_eval_sample = pd.DataFrame(
        {
            "eval_number": ["E_1", "E_OK", "WRONG_FORMAT", "E_WRONG_TOO"],
            "eval_feature": ["x1", "x2", "x3", "x4"],
        }
    )
    df_sondage_sample = pd.DataFrame({"id_employee": ["1", "OK"]})
    mock_read_csv.side_effect = [df_sirh_sample, df_eval_sample, df_sondage_sample]

    merged_df = load_and_merge_csvs()

    # S'assurer que le warning pour les eval_number mal formatés a été loggué.
    # 2 eval_number sont incorrects ('WRONG_FORMAT' ne commence pas par 'E_', 'E_WRONG_TOO' ne peut pas être converti car pas de _?)
    # La logique de split('_').str[1] va lever une erreur ou retourner NaN si pas de '_'.
    # pd.to_numeric(..., errors='coerce') transformera ces erreurs en NaN.
    # Ici, 'WRONG_FORMAT' et 'E_WRONG_TOO' devraient produire des NaN pour 'id_employee' dans df_eval.
    expected_warning_msg = "3 'eval_number' (après extraction) n'ont pas pu être convertis en id_employee numériques valides et sont devenus NaN."
    mock_logger.warning.assert_any_call(expected_warning_msg)
    # mock_logger.warning.assert_any_call("3 'eval_number' n'ont pas pu être convertis en 'id_employee' valides.")
    assert merged_df is not None
    # La ligne avec id_employee '1' devrait avoir eval_feature 'x1'
    assert (
        merged_df.loc[merged_df["id_employee"] == "1", "eval_feature"].iloc[0] == "x1"
    )
    # La ligne avec id_employee 'bad_id_format' ne trouvera pas de correspondance dans df_eval et aura NaN pour eval_feature
    assert pd.isna(
        merged_df.loc[merged_df["id_employee"] == "bad_id_format", "eval_feature"].iloc[
            0
        ]
    )
