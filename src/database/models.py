from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func # Pour func.now()
from .database_setup import Base # Importer la Base depuis database_setup.py

class Employee(Base):
    __tablename__ = "employees"

    id_employee = Column(String, primary_key=True, index=True)
    age = Column(Integer, nullable=True)
    genre = Column(String, nullable=True) # Ou Integer si déjà mappé
    revenu_mensuel = Column(Float, nullable=True)
    statut_marital = Column(String, nullable=True)
    departement = Column(String, nullable=True)
    poste = Column(String, nullable=True)
    nombre_experiences_precedentes = Column(Integer, nullable=True)
    annees_dans_l_entreprise = Column(Integer, nullable=True)
    satisfaction_employee_environnement = Column(Integer, nullable=True)
    note_evaluation_precedente = Column(Integer, nullable=True)
    satisfaction_employee_nature_travail = Column(Integer, nullable=True)
    satisfaction_employee_equipe = Column(Integer, nullable=True)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=True)
    note_evaluation_actuelle = Column(Integer, nullable=True)
    heure_supplementaires = Column(String, nullable=True)
    augementation_salaire_precedente = Column(Float, nullable=True)
    nombre_participation_pee = Column(Integer, nullable=True)
    nb_formations_suivies = Column(Integer, nullable=True)
    distance_domicile_travail = Column(Integer, nullable=True)
    niveau_education = Column(String, nullable=True)
    domaine_etude = Column(String, nullable=True)
    frequence_deplacement = Column(String, nullable=True)
    annees_depuis_la_derniere_promotion = Column(Integer, nullable=True)
    a_quitte_l_entreprise_numeric = Column(Integer, nullable=True)
    date_creation_enregistrement = Column(DateTime(timezone=True), server_default=func.now())
    date_derniere_modification = Column(DateTime(timezone=True), onupdate=func.now())


class ApiPredictionLog(Base):
    __tablename__ = "api_prediction_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp_requete = Column(DateTime(timezone=True), server_default=func.now())
    # employee_id_concerne peut être une clé étrangère si pertinent et si employee_id est unique et stable
    # employee_id_concerne = Column(String, ForeignKey("employees.employee_id"), nullable=True) 
    employee_id_concerne = Column(String, nullable=True, index=True)
    input_data = Column(JSON, nullable=False) # Stocker le JSON brut de l'input
    prediction_probabilite = Column(Float, nullable=False)
    prediction_classe = Column(Integer, nullable=False)
    version_modele = Column(String, nullable=True) # Pour la traçabilité