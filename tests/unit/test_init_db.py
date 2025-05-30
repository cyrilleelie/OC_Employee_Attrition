import pytest
from unittest.mock import patch, MagicMock
from src.database.init_db import create_tables

@patch('src.database.init_db.Base') # Mocker Base là où create_tables le voit
@patch('src.database.init_db.engine') # Mocker engine là où create_tables le voit
@patch('src.database.init_db.logger') # Mocker le logger pour vérifier les appels
def test_create_tables_success(mock_logger, mock_engine, mock_Base):
    """Teste que create_tables appelle Base.metadata.create_all et logue le succès."""
    # Configurer le mock de Base.metadata.create_all
    mock_metadata = MagicMock()
    mock_Base.metadata = mock_metadata

    create_tables()

    mock_metadata.create_all.assert_called_once_with(bind=mock_engine)
    mock_logger.info.assert_any_call("Tentative de création des tables dans la base de données...")
    mock_logger.info.assert_any_call("Tables créées avec succès (si elles n'existaient pas déjà).")

@patch('src.database.init_db.Base')
@patch('src.database.init_db.engine')
@patch('src.database.init_db.logger')
def test_create_tables_exception(mock_logger, mock_engine, mock_Base):
    """Teste la gestion d'exception si create_all échoue."""
    mock_metadata = MagicMock()
    mock_Base.metadata = mock_metadata
    mock_metadata.create_all.side_effect = Exception("DB error") # Simuler une erreur

    with pytest.raises(Exception, match="DB error"):
        create_tables()

    mock_metadata.create_all.assert_called_once_with(bind=mock_engine)
    mock_logger.info.assert_any_call("Tentative de création des tables dans la base de données...")
    mock_logger.error.assert_called_once_with("Erreur lors de la création des tables : DB error")