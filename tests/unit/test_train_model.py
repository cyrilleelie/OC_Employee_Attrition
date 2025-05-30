import pytest
from unittest.mock import patch, MagicMock, ANY
import pandas as pd
import numpy as np
from src.modeling.train_model import train_and_evaluate_pipeline
from src import config # Pour les mappings et la cible

@patch('src.modeling.train_model.dump') # joblib.dump
@patch('src.modeling.train_model.confusion_matrix', return_value=np.array([[0,0],[0,0]]))
@patch('src.modeling.train_model.fbeta_score', return_value=0.5)
@patch('src.modeling.train_model.classification_report', return_value="Mocked Report")
@patch('src.modeling.train_model.Pipeline') # sklearn.pipeline.Pipeline
@patch('src.modeling.train_model.LogisticRegression') # sklearn.linear_model.LogisticRegression
@patch('src.modeling.train_model.build_preprocessor')
@patch('src.modeling.train_model.create_features') # de preprocess
@patch('src.modeling.train_model.map_binary_features') # de preprocess
@patch('src.modeling.train_model.clean_data') # de preprocess
@patch('src.modeling.train_model.get_data') # de load_data
@patch('src.modeling.train_model.logger')
def test_train_and_evaluate_pipeline_success_path(
    mock_logger, mock_get_data, mock_clean_data, mock_map_binary, mock_create_features,
    mock_build_preprocessor, mock_LogisticRegression, mock_Pipeline,
    mock_classification_report, mock_fbeta_score, mock_confusion_matrix, mock_joblib_dump
):
    """Teste le chemin principal de train_and_evaluate_pipeline avec des mocks."""
    # 1. Configurer les mocks
    # Mock get_data pour retourner des données avec ASSEZ DE LIGNES
    sample_df_from_db = pd.DataFrame({
        'id_employee': [str(i) for i in range(1, 11)], # 10 lignes
        config.TARGET_VARIABLE: [0, 1, 0, 1, 0, 1, 0, 1, 0, 0], # 4 de classe 1, 6 de classe 0
        'genre':               [0, 1, 0, 1, 0, 1, 0, 1, 0, 1], # Alterner pour avoir des valeurs
        'heure_supplementaires': [0, 1, 0, 0, 1, 1, 0, 0, 1, 0],
        'frequence_deplacement': ['Non-Travel', 'Travel_Rarely', 'Travel_Frequently', 'Non-Travel', 'Travel_Rarely',
                                  'Non-Travel', 'Travel_Rarely', 'Travel_Frequently', 'Non-Travel', 'Travel_Rarely'],
        'age':                   [30, 45, 22, 50, 38, 29, 54, 33, 41, 47],
        'salaire_mensuel_brut':  [5000, 8000, 3500, 9000, 6000, 4800, 9500, 5500, 7000, 8200.0],
        'department':            ['Ventes', 'R&D', 'Ventes', 'Marketing', 'R&D',
                                  'Ventes', 'R&D', 'Ventes', 'Marketing', 'R&D'],
        'augmentation_salaire_precedente': [10.0, 15.0, 5.0, 12.0, 8.0, 9.0, 11.0, 6.0, 13.0, 7.0]
    })
    mock_get_data.return_value = sample_df_from_db

    df_after_features = sample_df_from_db.copy()
    mock_create_features.return_value = df_after_features
    
    mock_preprocessor_instance = MagicMock()
    mock_build_preprocessor.return_value = (mock_preprocessor_instance, ['mock_col1', 'mock_col2']) # Exemple

    mock_classifier_instance = MagicMock()
    mock_LogisticRegression.return_value = mock_classifier_instance

    mock_pipeline_instance = MagicMock()
    # Avec 10 lignes et test_size=0.2, X_test aura 2 lignes (10 * 0.2 = 2)
    # X_train aura 8 lignes.
    # Les mocks pour predict et predict_proba doivent donc retourner pour 2 échantillons
    mock_pipeline_instance.predict.return_value = np.array([0, 1]) 
    mock_pipeline_instance.predict_proba.return_value = np.array([[0.9, 0.1], [0.4, 0.6]])
    mock_Pipeline.return_value = mock_pipeline_instance

    # Appeler la fonction
    train_and_evaluate_pipeline()

    # 3. Assertions
    mock_get_data.assert_called_once_with(source="postgres")
    
    # Si vous avez bien enlevé les appels à clean_data et map_binary_features de train_model.py :
    mock_clean_data.assert_not_called()
    mock_map_binary.assert_not_called()
    # Si create_features est toujours appelé :
    mock_create_features.assert_called_once_with(sample_df_from_db) # Ou df_for_training avant le copy
    
    mock_build_preprocessor.assert_called_once()
    mock_LogisticRegression.assert_called_once_with(random_state=42, class_weight='balanced', max_iter=1000)
    # Par exemple, les appels à predict et predict_proba se feront sur X_test qui a 2 lignes
    mock_pipeline_instance.predict.assert_called_once() 
    # On peut vérifier la forme de l'argument avec lequel predict a été appelé
    # args_predict, _ = mock_pipeline_instance.predict.call_args
    # assert args_predict[0].shape[0] == 2 # X_test doit avoir 2 lignes

    # mock_pipeline_instance.predict_proba.assert_called_once()
    # args_proba, _ = mock_pipeline_instance.predict_proba.call_args
    # assert args_proba[0].shape[0] == 2 # X_test doit avoir 2 lignes
    mock_joblib_dump.assert_called_once_with(mock_pipeline_instance, config.MODEL_PATH)


@patch('src.modeling.train_model.get_data', return_value=None) # Simule un échec de chargement
@patch('src.modeling.train_model.logger')
def test_train_and_evaluate_pipeline_get_data_returns_none(mock_logger, mock_get_data_none):
    """Teste le cas où get_data retourne None."""
    train_and_evaluate_pipeline()
    mock_logger.error.assert_called_once_with("Arrêt : Impossible de charger les données ou DataFrame vide.")


@patch('src.modeling.train_model.get_data')
@patch('src.modeling.train_model.logger')
def test_train_and_evaluate_pipeline_get_data_returns_empty_df(mock_logger, mock_get_data_empty):
    """Teste le cas où get_data retourne un DataFrame vide."""
    mock_get_data_empty.return_value = pd.DataFrame() # df vide
    train_and_evaluate_pipeline() # Devrait maintenant appeler logger.error et return
    mock_logger.error.assert_called_once_with("Arrêt : Impossible de charger les données ou DataFrame vide.")
