from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union


# IMPORTANT : Ce modèle doit contenir TOUTES les features
# que votre modèle attend en entrée (AVANT preprocessing).
# Utilisez les mêmes noms que dans vos fichiers CSV initiaux.
# Ajoutez des descriptions et des exemples pour une meilleure documentation.
class EmployeeInput(BaseModel):
    age: int = Field(
        ..., json_schema_extra={"example": 41}, description="Âge de l'employé"
    )
    genre: str = Field(
        ..., json_schema_extra={"example": "F"}, description="Genre ('M' ou 'F')"
    )
    revenu_mensuel: float = Field(
        ..., json_schema_extra={"example": 5993.0}, description="Revenu mensuel"
    )
    statut_marital: str = Field(
        ..., json_schema_extra={"example": "Célibataire"}, description="Statut marital"
    )
    departement: str = Field(
        ...,
        json_schema_extra={"example": "Commercial"},
        description="Département de l'entreprise",
    )
    poste: str = Field(
        ...,
        json_schema_extra={"example": "Cadre Commercial"},
        description="Titre du poste",
    )
    nombre_experiences_precedentes: int = Field(
        ...,
        json_schema_extra={"example": 8},
        description="Nombre d'expériences précédentes",
    )
    annees_dans_l_entreprise: int = Field(
        ..., json_schema_extra={"example": 5}, description="Années d'ancienneté"
    )
    satisfaction_employee_environnement: int = Field(
        ...,
        json_schema_extra={"example": 4},
        description="Satisfaction de l'employé concernant l'environnement de travail (1-4)",
    )
    satisfaction_employee_nature_travail: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Satisfaction de l'employé concernant la nature du travail (1-4)",
    )
    satisfaction_employee_equipe: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Satisfaction de l'employé concernant l'équipe (1-4)",
    )
    satisfaction_employee_equilibre_pro_perso: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Satisfaction de l'employé concernant l'équilibre pro/perso (1-4)",
    )
    note_evaluation_precedente: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Note d'évaluation précédente de l'employé (1-4)",
    )
    note_evaluation_actuelle: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Note d'évaluation actuelle de l'employé (1-4)",
    )
    heure_supplementaires: str = Field(
        ...,
        json_schema_extra={"example": "Oui"},
        description="Fait des heures supplémentaires ('Oui' ou 'Non')",
    )
    augementation_salaire_precedente: str = Field(
        ...,
        json_schema_extra={"example": "11 %"},
        description="Pourcentage d'augmentation N-1 (format 'XX %')",
    )
    nombre_participation_pee: int = Field(
        ...,
        json_schema_extra={"example": 0},
        description="Nombre de participations au PEE",
    )
    nb_formations_suivies: int = Field(
        ...,
        json_schema_extra={"example": 2},
        description="Nombre de formations suivies",
    )
    distance_domicile_travail: int = Field(
        ..., json_schema_extra={"example": 1}, description="Distance en km"
    )
    niveau_education: int = Field(
        ..., json_schema_extra={"example": 3}, description="Niveau d'éducation (1-5)"
    )
    domaine_etude: str = Field(
        ...,
        json_schema_extra={"example": "Infra & Cloud"},
        description="Domaine d'études",
    )
    frequence_deplacement: str = Field(
        ...,
        json_schema_extra={"example": "Occasionnel"},
        description="Fréquence ('Aucun', 'Occasionnel', 'Frequent')",
    )
    annees_depuis_la_derniere_promotion: int = Field(
        ...,
        json_schema_extra={"example": 0},
        description="Nombre d'années depuis la dernière promotion'",
    )

    # Permet de définir un exemple visible dans la documentation Swagger
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 45,
                "genre": "M",
                "revenu_mensuel": 4850,
                "statut_marital": "Célibataire",
                "departement": "Commercial",
                "poste": "Cadre Commercial",
                "nombre_experiences_precedentes": 8,
                "annees_dans_l_entreprise": 5,
                "satisfaction_employee_environnement": 4,
                "note_evaluation_precedente": 3,
                "satisfaction_employee_nature_travail": 3,
                "satisfaction_employee_equipe": 3,
                "satisfaction_employee_equilibre_pro_perso": 3,
                "note_evaluation_actuelle": 3,
                "heure_supplementaires": "Oui",
                "augementation_salaire_precedente": "15 %",
                "nombre_participation_pee": 0,
                "nb_formations_suivies": 3,
                "distance_domicile_travail": 20,
                "niveau_education": 3,
                "domaine_etude": "Infra & Cloud",
                "frequence_deplacement": "Occasionnel",
                "annees_depuis_la_derniere_promotion": 0,
            }
        }
    )


# Schéma pour la réponse de prédiction
class PredictionOutput(BaseModel):
    id_employe: Union[str, int]  # L'ID peut être un str ou un int
    probabilite_depart: float = Field(
        ...,
        json_schema_extra={"example": 0.65},
        description="Probabilité de départ (0 à 1)",
    )
    prediction_depart: int = Field(
        ...,
        json_schema_extra={"example": 1},
        description="Prédiction (0 = Reste, 1 = Part)",
    )


# Schéma pour les requêtes en masse
class BulkPredictionInput(BaseModel):
    employees: List[EmployeeInput]


# Schéma pour les réponses en masse
class BulkPredictionOutput(BaseModel):
    predictions: List[PredictionOutput]
