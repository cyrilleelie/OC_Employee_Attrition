"""
Script pour initialiser la base de données.

Ce module contient la logique pour créer toutes les tables définies
dans les modèles SQLAlchemy (via src.database.models) dans la base de données
configurée (via src.database.database_setup.engine).

Ce script est généralement exécuté une fois pour mettre en place le schéma
de la base de données, ou après des modifications de schéma si les tables
doivent être recréées (attention, la recréation peut entraîner une perte de données
si les tables existent déjà et ne sont pas vidées au préalable).
"""

import logging
from sqlalchemy.exc import (
    SQLAlchemyError,
)  # Pour une capture d'exception plus spécifique

# Importe l'engine SQLAlchemy et la Base déclarative
from src.database.database_setup import engine, Base

# Importez explicitement TOUS vos modèles SQLAlchemy ici.
# Cela garantit qu'ils sont bien enregistrés avec la métadonnée de 'Base'
# avant que 'Base.metadata.create_all()' ne soit appelé.

# Configuration de base du logging pour ce script
# Si vous avez une configuration de logging centralisée, vous pourriez l'utiliser à la place.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_tables():
    """
    Crée toutes les tables définies dans les modèles SQLAlchemy.

    Utilise l'objet `engine` global et la métadonnée de `Base` pour émettre
    les commandes DDL (Data Definition Language) appropriées afin de créer
    les tables dans la base de données si elles n'existent pas déjà.

    Enregistre des messages d'information sur le succès ou l'échec de l'opération.

    Raises:
        SQLAlchemyError: Si une erreur se produit lors de l'interaction avec la base de données
                         pendant la création des tables.
    """
    logger.info("Tentative de création des tables dans la base de données...")
    try:
        # Employee et ApiPredictionLog sont maintenant connus de Base.metadata
        # grâce à leurs imports ci-dessus.
        Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès (ou déjà existantes).")
    except SQLAlchemyError as e:  # Capture d'erreur plus spécifique
        logger.error(
            f"Erreur SQLAlchemy lors de la création des tables : {e}", exc_info=True
        )
        raise  # Relance l'exception pour que l'appelant soit informé
    except Exception as e:  # Capture d'autres exceptions potentielles
        logger.error(
            f"Erreur inattendue lors de la création des tables : {e}", exc_info=True
        )
        raise


if __name__ == "__main__":
    # Ce bloc s'exécute uniquement lorsque le script est lancé directement
    # (par exemple, via `python -m src.database.init_db`)
    logger.info("--- Initialisation du schéma de la base de données ---")
    create_tables()
    logger.info("--- Schéma de la base de données initialisé ---")
