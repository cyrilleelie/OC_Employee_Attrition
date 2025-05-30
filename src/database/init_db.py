# Dans src/database/init_db.py
import logging
from src.database.database_setup import engine, Base
# Importez explicitement TOUS vos modèles ici pour vous assurer
# qu'ils sont enregistrés avec la métadonnée de Base avant create_all
from src.database.models import Employee, ApiPredictionLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    logger.info("Tentative de création des tables dans la base de données...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès (si elles n'existaient pas déjà).")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables : {e}")
        raise

if __name__ == "__main__":
    create_tables()