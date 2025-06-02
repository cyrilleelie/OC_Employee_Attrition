import pytest
from unittest.mock import patch, MagicMock
from src.database.init_db import create_tables
from sqlalchemy.exc import SQLAlchemyError


@patch("src.database.init_db.Base")  # Mocker Base là où create_tables le voit
@patch("src.database.init_db.engine")  # Mocker engine là où create_tables le voit
@patch("src.database.init_db.logger")  # Mocker le logger pour vérifier les appels
def test_create_tables_success(mock_logger, mock_engine, mock_Base):
    """Teste que create_tables appelle Base.metadata.create_all et logue le succès."""
    # Configurer le mock de Base.metadata.create_all
    mock_metadata = MagicMock()
    mock_Base.metadata = mock_metadata

    create_tables()

    mock_metadata.create_all.assert_called_once_with(bind=mock_engine)
    mock_logger.info.assert_any_call(
        "Tentative de création des tables dans la base de données..."
    )
    mock_logger.info.assert_any_call("Tables créées avec succès (ou déjà existantes).")


@patch("src.database.init_db.Base")
@patch("src.database.init_db.engine")
@patch(
    "src.database.init_db.logger"
)  # Assurez-vous que c'est le bon chemin pour le logger utilisé dans init_db.py
def test_create_tables_exception(mock_logger, mock_engine, mock_Base):
    """Teste la gestion d'exception si create_all échoue avec une exception générique."""
    mock_metadata = MagicMock()
    mock_Base.metadata = mock_metadata

    # Simuler une erreur générique
    simulated_exception = Exception("DB error")
    mock_metadata.create_all.side_effect = simulated_exception

    with pytest.raises(
        Exception, match="DB error"
    ):  # Vérifie que l'exception est bien relevée
        create_tables()

    mock_metadata.create_all.assert_called_once_with(bind=mock_engine)
    mock_logger.info.assert_any_call(
        "Tentative de création des tables dans la base de données..."
    )

    # Mettre à jour l'assertion pour le message d'erreur et l'argument exc_info
    expected_error_message = (
        f"Erreur inattendue lors de la création des tables : {simulated_exception}"
    )
    mock_logger.error.assert_called_once_with(expected_error_message, exc_info=True)


@patch("src.database.init_db.Base")
@patch("src.database.init_db.engine")
@patch("src.database.init_db.logger")
def test_create_tables_sqlalchemy_exception(mock_logger, mock_engine, mock_Base):
    """Teste la gestion d'exception si create_all échoue avec une SQLAlchemyError."""
    mock_metadata = MagicMock()
    mock_Base.metadata = mock_metadata

    simulated_sqlalchemy_exception = SQLAlchemyError("SQLAlchemy specific error")
    mock_metadata.create_all.side_effect = simulated_sqlalchemy_exception

    # On s'attend à ce que SQLAlchemyError soit relevée (ou une de ses sous-classes)
    with pytest.raises(SQLAlchemyError, match="SQLAlchemy specific error"):
        create_tables()

    mock_metadata.create_all.assert_called_once_with(bind=mock_engine)
    mock_logger.info.assert_any_call(
        "Tentative de création des tables dans la base de données..."
    )

    expected_error_message = f"Erreur SQLAlchemy lors de la création des tables : {simulated_sqlalchemy_exception}"
    mock_logger.error.assert_called_once_with(expected_error_message, exc_info=True)
