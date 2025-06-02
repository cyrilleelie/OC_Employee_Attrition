"""
Définition des modèles SQLAlchemy ORM pour les tables de la base de données.

Ce module contient les classes Python qui mappent aux tables de la base de données
PostgreSQL, en utilisant la Base déclarative de SQLAlchemy.
Chaque classe représente une table, et ses attributs de classe représentent
les colonnes de cette table.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import NUMERIC  # Pour un type monétaire plus précis
from sqlalchemy.sql import func  # Pour les valeurs par défaut SQL comme func.now()
from .database_setup import Base  # Importer la Base depuis database_setup.py


class Employee(Base):
    """
    Modèle SQLAlchemy représentant un employé et ses caractéristiques.
    Mappe à la table 'employees' dans la base de données.
    Cette table contient les données fusionnées et prétraitées utilisées
    pour l'entraînement du modèle d'attrition et potentiellement pour
    enrichir les informations lors des prédictions.
    """

    __tablename__ = "employees"

    # Clé primaire : identifiant unique de l'employé
    id_employee = Column(
        String(255), primary_key=True, index=True
    )  # Longueur spécifiée pour VARCHAR

    # Caractéristiques de l'employé
    age = Column(Integer, nullable=True)
    genre = Column(
        String(50), nullable=True
    )  # Ex: "M", "F" ou 0, 1 si déjà mappé avant BDD
    # Pour les revenus, NUMERIC est souvent préférable à Float pour la précision exacte.
    # NUMERIC(precision, scale) : precision = nombre total de chiffres, scale = nombre de chiffres après la virgule.
    revenu_mensuel = Column(NUMERIC(10, 2), nullable=True)
    statut_marital = Column(String(50), nullable=True)
    departement = Column(String(100), nullable=True)
    poste = Column(String(100), nullable=True)
    nombre_experiences_precedentes = Column(Integer, nullable=True)
    annees_dans_l_entreprise = Column(
        Integer, nullable=True
    )  # Pourrait être Float si fractions d'années

    # Scores de satisfaction et évaluations (typiquement des échelles entières)
    satisfaction_employee_environnement = Column(Integer, nullable=True)
    note_evaluation_precedente = Column(
        Integer, nullable=True
    )  # Ou Float si les notes peuvent être décimales
    satisfaction_employee_nature_travail = Column(Integer, nullable=True)
    satisfaction_employee_equipe = Column(Integer, nullable=True)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=True)
    note_evaluation_actuelle = Column(Integer, nullable=True)  # Ou Float

    heure_supplementaires = Column(
        String(10), nullable=True
    )  # Ex: "Oui", "Non" ou 0, 1
    augementation_salaire_precedente = Column(
        Float, nullable=True
    )  # Stocké comme float (ex: 10.0 pour 10%)
    nombre_participation_pee = Column(Integer, nullable=True)
    nb_formations_suivies = Column(Integer, nullable=True)
    distance_domicile_travail = Column(Integer, nullable=True)  # Ou Float

    niveau_education = Column(String(100), nullable=True)
    domaine_etude = Column(String(100), nullable=True)
    frequence_deplacement = Column(
        String(50), nullable=True
    )  # Ex: "Non-Travel", "Travel_Rarely"

    annees_depuis_la_derniere_promotion = Column(Integer, nullable=True)

    # Variable cible
    a_quitte_l_entreprise_numeric = Column(Integer, nullable=True)  # 0 ou 1

    # Timestamps pour le suivi des enregistrements
    date_creation_enregistrement = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Valeur par défaut au niveau SQL lors de l'INSERT
        nullable=False,
    )
    date_derniere_modification = Column(
        DateTime(timezone=True),
        default=func.now(),  # Valeur par défaut côté application lors de l'INSERT
        onupdate=func.now(),  # Valeur mise à jour côté application lors d'un UPDATE
        nullable=False,
    )


class ApiPredictionLog(Base):
    """
    Modèle SQLAlchemy pour enregistrer les appels à l'API de prédiction.
    Mappe à la table 'api_prediction_logs'. Chaque enregistrement correspond
    à une requête de prédiction, incluant les données d'entrée et le résultat.
    """

    __tablename__ = "api_prediction_logs"

    # Clé primaire auto-incrémentée pour le log
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Timestamp de la requête
    timestamp_requete = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Identifiant de l'employé concerné par la prédiction, si applicable.
    # Peut être lié à la table 'employees' via une clé étrangère pour l'intégrité référentielle.
    # employee_id_concerne = Column(String(255), ForeignKey("employees.id_employee"), nullable=True, index=True)
    employee_id_concerne = Column(
        String(255), nullable=True, index=True
    )  # Gardé comme String pour l'instant

    # Données d'entrée JSON brutes envoyées à l'API
    input_data = Column(JSON, nullable=False)

    # Résultats de la prédiction
    prediction_probabilite = Column(Float, nullable=False)
    prediction_classe = Column(Integer, nullable=False)  # 0 ou 1

    # Version du modèle utilisé pour la prédiction (pour la traçabilité)
    version_modele = Column(String(100), nullable=True)  # Longueur augmentée
