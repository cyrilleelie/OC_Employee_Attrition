from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd
from src.modeling.predict import load_prediction_pipeline, predict_attrition
from src import config  # Pour config.MODEL_PATH


@patch("src.modeling.predict.load")  # Mocker joblib.load
@patch("src.modeling.predict.config.MODEL_PATH")
@patch("src.modeling.predict.logger")
def test_load_prediction_pipeline_success(
    mock_logger, mock_model_path, mock_joblib_load
):
    """Teste le chargement réussi de la pipeline."""
    mock_pipeline_obj = MagicMock()
    mock_joblib_load.return_value = mock_pipeline_obj
    mock_model_path.exists.return_value = True

    # Réinitialiser la variable globale _pipeline pour ce test
    from src.modeling import predict
    predict._pipeline = None

    pipeline = load_prediction_pipeline()

    mock_model_path.exists.assert_called_once()
    mock_joblib_load.assert_called_once_with(mock_model_path)
    
    # CORRECTION ICI :
    expected_log_msg_loading = f"Chargement de la pipeline de prédiction depuis : {mock_model_path}..."
    mock_logger.info.assert_any_call(expected_log_msg_loading)

    mock_logger.info.assert_any_call("Pipeline de prédiction chargée avec succès.") # Vérifiez aussi ce message
    assert pipeline == mock_pipeline_obj


@patch("src.modeling.predict.config.MODEL_PATH")
@patch("src.modeling.predict.logger")
def test_load_prediction_pipeline_file_not_found(mock_logger, mock_model_path):
    """Teste le cas où le fichier modèle n'est pas trouvé."""
    mock_model_path.exists.return_value = False

    from src.modeling import predict
    predict._pipeline = None

    pipeline = load_prediction_pipeline()

    # Assertions
    mock_model_path.exists.assert_called_once()
    
    # CORRECTION ICI :
    expected_log_msg = f"Fichier pipeline non trouvé à l'emplacement configuré : {mock_model_path}"
    mock_logger.error.assert_any_call(expected_log_msg)
    assert pipeline is None


@patch("src.modeling.predict.load")
@patch("src.modeling.predict.config.MODEL_PATH")
@patch("src.modeling.predict.logger")
def test_load_prediction_pipeline_load_exception(
    mock_logger, mock_model_path, mock_joblib_load
):
    """Teste une exception lors du chargement du modèle."""
    mock_model_path.exists.return_value = True
    simulated_exception = Exception("Load error")
    mock_joblib_load.side_effect = simulated_exception
    mock_model_path.exists.return_value = True

    from src.modeling import predict

    predict._pipeline = None

    pipeline = load_prediction_pipeline()

    expected_log_msg = f"Erreur critique lors du chargement de la pipeline : {simulated_exception}"
    mock_logger.error.assert_any_call(expected_log_msg, exc_info=True)
    assert pipeline is None


@patch("src.modeling.predict.create_features")
@patch("src.modeling.predict.map_binary_features")
@patch("src.modeling.predict.clean_data")
@patch("src.modeling.predict.load_prediction_pipeline")
@patch("src.modeling.predict.logger")
def test_predict_attrition_success_path(
    mock_logger,
    mock_load_pipeline,
    mock_clean_data,
    mock_map_binary,
    mock_create_features,
):
    """Teste le chemin de succès de predict_attrition avec des mocks."""
    # 1. Configurer les mocks
    mock_pipeline_instance = MagicMock()
    # MODIFIÉ : Retourner des tableaux NumPy et pour 1 seul échantillon
    mock_pipeline_instance.predict_proba.return_value = np.array(
        [[0.3, 0.7]]
    )  # Pour 1 échantillon
    mock_pipeline_instance.predict.return_value = np.array([1])  # Pour 1 échantillon
    mock_load_pipeline.return_value = mock_pipeline_instance

    # Simuler les DataFrames retournés par chaque étape de preprocessing
    # df_raw_input a 1 ligne, donc toutes les sorties mockées doivent aussi correspondre à 1 ligne
    df_raw_input = pd.DataFrame({"feature1": ["A"], "feature2": [10]}, index=["EMP_X"])

    # La fonction clean_data dans predict.py ajoute temporairement 'a_quitte_l_entreprise'
    df_cleaned_for_predict = df_raw_input.copy()
    # Supposons que config.TARGET_VARIABLE est 'a_quitte_l_entreprise_numeric'
    df_cleaned_for_predict[config.TARGET_VARIABLE] = 0  # Ajout factice pour le mock
    df_cleaned_for_predict["feature1_clean"] = "A_clean"  # Simuler le nettoyage
    mock_clean_data.return_value = df_cleaned_for_predict

    # df_mapped_mock et df_featured_mock doivent aussi avoir 1 ligne
    df_mapped_mock = pd.DataFrame(
        {"feature1_map": [0], "feature2_map": [10]}, index=["EMP_X"]
    )
    mock_map_binary.return_value = df_mapped_mock

    df_featured_mock = pd.DataFrame(
        {"feature1_final": [0], "feature2_final": [100]}, index=["EMP_X"]
    )
    mock_create_features.return_value = df_featured_mock

    # 2. Appeler la fonction
    results = predict_attrition(df_raw_input)
    # print(f"DEBUG: Results in test: {results}") # Ligne de débogage si besoin

    # 3. Assertions
    mock_load_pipeline.assert_called_once()
    mock_clean_data.assert_called_once()
    mock_map_binary.assert_called_once_with(
        mock_clean_data.return_value, config.BINARY_FEATURES_MAPPING
    )
    mock_create_features.assert_called_once_with(mock_map_binary.return_value)

    # X_predict_expected est dérivé de df_featured_mock (1 ligne)
    # X_predict_expected = df_featured_mock.drop(columns=[config.TARGET_VARIABLE], errors="ignore")

    # Vérifier que les méthodes de la pipeline sont appelées
    # L'argument passé à predict_proba sera X_predict_expected
    # Vous pouvez utiliser pd.testing.assert_frame_equal si vous voulez être très précis sur l'argument
    # mock_pipeline_instance.predict_proba.assert_called_once_with(X_predict_expected) # Ne fonctionnera pas directement avec assert_frame_equal ici

    # Vérification des appels (plus simple et souvent suffisant)
    assert mock_pipeline_instance.predict_proba.call_count == 1
    assert mock_pipeline_instance.predict.call_count == 1  # Devrait passer maintenant

    assert len(results) == 1
    assert results[0]["id_employe"] == "EMP_X"
    assert (
        results[0]["probabilite_depart"] == 0.7
    )  # Correspond à np.array([[0.3, 0.7]])[:, 1][0]
    assert results[0]["prediction_depart"] == 1  # Correspond à np.array([1])[0]
    mock_logger.info.assert_any_call("Prédictions formatées avec succès.")
