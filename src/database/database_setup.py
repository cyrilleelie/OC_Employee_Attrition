"""
Configuration centrale de SQLAlchemy pour la connexion à la base de données.

Ce module initialise l'objet `engine` de SQLAlchemy, la fabrique de sessions `SessionLocal`, et la classe de base déclarative `Base` pour les modèles ORM. Il fournit également une fonction de dépendance (`get_db`) pour FastAPI afin de gérer les sessions de base de données par requête.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    Session as SQLAlchemySession,
)  # Pour le type hint
from typing import Generator  # Pour le type hint de get_db

from src import config  # Pour récupérer DATABASE_URL

# L'URL de connexion à la base de données, récupérée depuis la configuration.
# Format attendu : "postgresql://utilisateur:motdepasse@hote:port/nom_base_de_donnees"
SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

# Crée l'objet Engine de SQLAlchemy.
# C'est le point d'entrée principal pour la communication avec la base de données.
# Il gère le pool de connexions et le dialecte spécifique à PostgreSQL.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crée une classe SessionLocal, qui est une fabrique de sessions.
# Chaque instance de SessionLocal sera une session de base de données transactionnelle.
# - autocommit=False: Les changements ne sont pas commités automatiquement.
# - autoflush=False: Les objets ne sont pas envoyés à la BDD avant le commit explicite.
# - bind=engine: Lie cette fabrique de sessions à notre engine PostgreSQL.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crée une classe Base pour les modèles ORM déclaratifs.
# Toutes les classes de modèles (ex: Employee, ApiPredictionLog) hériteront de cette Base.
# Elle contient la métadonnée qui décrit comment les classes Python sont mappées aux tables de la BDD.
Base = declarative_base()


# --- Fonction de création de tables ---
# NOTE : Vous avez une fonction similaire (voire identique) dans src/database/init_db.py.
# Il est généralement préférable d'avoir une seule source de vérité pour cette action.
# Vous pourriez soit supprimer cette fonction et laisser init_db.py gérer la création,
# soit faire en sorte que init_db.py appelle CETTE fonction.
# Pour l'instant, je documente celle-ci telle qu'elle est.
def create_db_tables():
    """
    Crée toutes les tables dans la base de données définies par les modèles
    qui héritent de `Base`.

    Cette fonction est idempotente : elle ne créera les tables que si elles
    n'existent pas déjà.
    """
    # Base.metadata contient toutes les informations sur les tables à créer.
    Base.metadata.create_all(bind=engine)


# --- Dépendance FastAPI pour les sessions de base de données ---
def get_db() -> Generator[SQLAlchemySession, None, None]:
    """
    Dépendance FastAPI pour obtenir une session de base de données SQLAlchemy.

    Ce générateur crée une nouvelle session de base de données pour chaque requête entrante,
    la fournit à la fonction de chemin (endpoint), puis s'assure qu'elle est fermée
    après que la requête a été traitée (même en cas d'erreur).

    Yields:
        SQLAlchemySession: Une session de base de données SQLAlchemy.
    """
    db = SessionLocal()  # Crée une nouvelle session
    try:
        yield db  # Fournit la session à la fonction de l'endpoint
    finally:
        db.close()  # S'assure que la session est toujours fermée après usage
