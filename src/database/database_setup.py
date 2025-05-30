from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src import config # Pour récupérer DATABASE_URL

# Créer l'objet Engine qui gère la connexion à la BDD
# config.DATABASE_URL devrait être du type "postgresql://user:password@host:port/dbname"
engine = create_engine(config.DATABASE_URL)

# Créer une SessionLocal class. Chaque instance de SessionLocal sera une session de base de données.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class pour nos modèles ORM. Toutes nos classes de modèles en hériteront.
Base = declarative_base()

# Fonction pour créer toutes les tables dans la base de données
# (si elles n'existent pas déjà)
def create_db_tables():
    Base.metadata.create_all(bind=engine)

# Dépendance pour les routes FastAPI afin d'obtenir une session BDD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()