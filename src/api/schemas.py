"""
Définition des schémas Pydantic pour la validation des données de l'API.

Ce module contient les modèles de données utilisés par FastAPI pour :
- Valider les données des requêtes entrantes.
- Sérialiser les données des réponses sortantes.
- Générer automatiquement la documentation OpenAPI (Swagger UI).
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Union

from src import config  # Importer votre module config

print("-" * 20)
print("DEBUG SCHEMAS: Chargement des configurations...")
print(
    f"Allowed genre keys from config: {list(config.BINARY_FEATURES_MAPPING['genre'].keys())}"
)
print(
    f"Allowed heure_supplementaires keys from config: {list(config.BINARY_FEATURES_MAPPING['heure_supplementaires'].keys())}"
)
print(
    f"Allowed frequence_deplacement values from config: {config.ORDINAL_FEATURES_CATEGORIES['frequence_deplacement']}"
)
print(
    f"Allowed statut_marital values from config: {config.LIMITED_VALUES_FEATURES['statut_marital']}"
)
print(
    f"Allowed departement values from config: {config.LIMITED_VALUES_FEATURES['departement']}"
)
print(f"Allowed poste values from config: {config.LIMITED_VALUES_FEATURES['poste']}")
print(
    f"Allowed domaine_etude values from config: {config.LIMITED_VALUES_FEATURES['domaine_etude']}"
)
print("-" * 20)


# IMPORTANT : Ce modèle doit contenir TOUTES les features
# que votre modèle attend en entrée (AVANT preprocessing).
# Utilisez les mêmes noms que dans vos fichiers CSV initiaux.
# Ajoutez des descriptions et des exemples pour une meilleure documentation.
class EmployeeInput(BaseModel):
    """
    Schéma Pydantic représentant les données d'entrée pour un employé
    lors d'une requête de prédiction d'attrition.

    Les champs correspondent aux données brutes attendues par la pipeline de preprocessing
    avant toute transformation majeure (scaling, one-hot encoding, etc.).
    Les descriptions et exemples aident à la compréhension et à l'utilisation de l'API.
    """

    age: int = Field(
        ...,  # Le "..." indique que le champ est requis
        json_schema_extra={"example": 41},
        description="Âge de l'employé en années.",
    )
    genre: str = Field(
        ...,
        json_schema_extra={
            "example": "F"
        },  # Modifié pour correspondre à la description
        description=f"Genre de l'employé. Valeurs attendues : {list(config.BINARY_FEATURES_MAPPING['genre'].keys())}",  # Préciser les valeurs attendues si possible
    )
    revenu_mensuel: float = Field(
        ...,
        json_schema_extra={"example": 5993.0},
        description="Revenu mensuel brut de l'employé.",
    )
    statut_marital: str = Field(
        ...,
        json_schema_extra={"example": "Célibataire"},
        description=f"Statut marital de l'employé. Valeurs attendues : {config.LIMITED_VALUES_FEATURES['statut_marital']}",
    )
    departement: str = Field(
        ...,
        json_schema_extra={
            "example": "Commercial"
        },  # 'Ventes' au lieu de 'Commercial' pour un département
        description=f"Département de l'entreprise où travaille l'employé. Valeurs attendues : {config.LIMITED_VALUES_FEATURES['departement']}",
    )
    poste: str = Field(
        ...,
        json_schema_extra={"example": "Cadre Commercial"},
        description=f"Intitulé du poste de l'employé. Valeurs attendues : {config.LIMITED_VALUES_FEATURES['poste']}",
    )
    nombre_experiences_precedentes: int = Field(
        ...,
        json_schema_extra={
            "example": 3
        },  # J'ai mis 3 au lieu de 8 pour varier de l'exemple global
        description="Nombre d'emplois précédents de l'employé avant l'actuel.",
    )
    annees_dans_l_entreprise: int = Field(
        ...,
        json_schema_extra={"example": 5},
        description="Nombre total d'années passées par l'employé dans l'entreprise actuelle.",
    )
    # Pour les scores de satisfaction, préciser l'échelle est une bonne idée.
    satisfaction_employee_environnement: int = Field(
        ...,
        json_schema_extra={"example": 4},
        description="Score de satisfaction de l'employé concernant l'environnement de travail (généralement sur une échelle de 1 à 5).",
    )
    satisfaction_employee_nature_travail: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Score de satisfaction de l'employé concernant la nature de son travail (échelle 1-5).",
    )
    satisfaction_employee_equipe: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Score de satisfaction de l'employé concernant son équipe (échelle 1-5).",
    )
    satisfaction_employee_equilibre_pro_perso: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Score de satisfaction de l'employé concernant son équilibre vie professionnelle/vie personnelle (échelle 1-5).",
    )
    note_evaluation_precedente: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Note obtenue lors de la dernière évaluation de performance (échelle 1-5).",
    )
    note_evaluation_actuelle: int = Field(
        ...,
        json_schema_extra={"example": 3},
        description="Note obtenue lors de l'évaluation de performance actuelle (échelle 1-5).",
    )
    heure_supplementaires: str = Field(
        ...,
        json_schema_extra={"example": "Oui"},
        description=f"Indique si l'employé effectue des heures supplémentaires. Valeurs attendues : {list(config.BINARY_FEATURES_MAPPING['heure_supplementaires'].keys())}",
    )
    augementation_salaire_precedente: str = (
        Field(  # Note: "augementation" a une petite coquille, devrait être "augmentation"
            ...,
            json_schema_extra={"example": "11 %"},
            description="Pourcentage de la dernière augmentation de salaire (format attendu: 'XX %').",
        )
    )
    nombre_participation_pee: int = Field(
        ...,
        json_schema_extra={"example": 0},
        description="Nombre de fois où l'employé a participé au Plan d'Épargne Entreprise (PEE).",
    )
    nb_formations_suivies: int = Field(
        ...,
        json_schema_extra={"example": 2},
        description="Nombre de formations suivies par l'employé récemment (ex: sur l'année N).",
    )
    distance_domicile_travail: int = Field(
        ...,
        json_schema_extra={"example": 10},  # Varié par rapport à l'exemple global
        description="Distance en kilomètres entre le domicile et le lieu de travail.",
    )
    niveau_education: int = (
        Field(  # Si c'est une échelle numérique (ex: 1=Bac, 2=Bac+2...)
            ...,
            json_schema_extra={"example": 3},
            description="Niveau d'éducation codifié (ex: 1 pour Bac, 2 pour Bac+2, ..., 5 pour Doctorat).",
        )
    )
    # OU si c'est textuel :
    # niveau_education: str = Field(
    #     ...,
    #     json_schema_extra={"example": "Master"},
    #     description="Plus haut niveau d'éducation atteint (ex: 'Licence', 'Master', 'Doctorat')."
    # )
    domaine_etude: str = Field(
        ...,
        json_schema_extra={"example": "Informatique"},  # Varié
        description=f"Domaine principal d'études de l'employé. Valeurs attendues : {config.LIMITED_VALUES_FEATURES['domaine_etude']}",
    )
    frequence_deplacement: str = Field(
        ...,
        json_schema_extra={"example": "Occasionnel"},
        description=f"Fréquence des déplacements professionnels. Valeurs attendues : {config.ORDINAL_FEATURES_CATEGORIES['frequence_deplacement']}",
    )
    annees_depuis_la_derniere_promotion: int = Field(
        ...,
        json_schema_extra={"example": 1},  # Varié
        description="Nombre d'années écoulées depuis la dernière promotion de l'employé.",
    )

    # --- VALIDATEURS ---
    @field_validator("genre")
    @classmethod
    def validate_genre(cls, value: str) -> str:
        allowed_values = config.BINARY_FEATURES_MAPPING["genre"].keys()
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'genre' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    @field_validator("heure_supplementaires")
    @classmethod
    def validate_heure_supplementaires(cls, value: str) -> str:
        allowed_values = config.BINARY_FEATURES_MAPPING["heure_supplementaires"].keys()
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'heure_supplementaires' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    @field_validator("frequence_deplacement")
    @classmethod
    def validate_frequence_deplacement(cls, value: str) -> str:
        allowed_values = config.ORDINAL_FEATURES_CATEGORIES["frequence_deplacement"]
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'frequence_deplacement' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    @field_validator("statut_marital")
    @classmethod
    def validate_statut_marital(cls, value: str) -> str:
        allowed_values = config.LIMITED_VALUES_FEATURES["statut_marital"]
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'statut_marital' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    @field_validator("departement")
    @classmethod
    def validate_departement(cls, value: str) -> str:
        allowed_values = config.LIMITED_VALUES_FEATURES["departement"]
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'departement' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    @field_validator("poste")
    @classmethod
    def validate_poste(cls, value: str) -> str:
        allowed_values = config.LIMITED_VALUES_FEATURES["poste"]
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'poste' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    @field_validator("domaine_etude")
    @classmethod
    def validate_domaine_etude(cls, value: str) -> str:
        allowed_values = config.LIMITED_VALUES_FEATURES["domaine_etude"]
        if value not in allowed_values:
            raise ValueError(
                f"Valeur pour 'domaine_etude' non valide. Doit être l'une de : {list(allowed_values)}"
            )
        return value

    # model_config pour Pydantic V2, remplace l'ancienne class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {  # Cet exemple est utilisé par Swagger UI pour pré-remplir le corps de la requête
                "age": 45,
                "genre": "M",  # Changé en "Homme" pour correspondre au format plus courant
                "revenu_mensuel": 4850.0,
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
                "niveau_education": 3,  # En supposant le format numérique pour l'exemple
                "domaine_etude": "Infra & Cloud",
                "frequence_deplacement": "Occasionnel",
                "annees_depuis_la_derniere_promotion": 0,
            }
        }
    )


class PredictionOutput(BaseModel):
    """
    Schéma Pydantic pour la réponse d'une requête de prédiction.
    Inclut l'identifiant de l'employé (tel que retourné par la logique de prédiction),
    la probabilité de départ, et la classe prédite.
    """

    id_employe: Union[
        str, int
    ]  # L'ID peut être un str (ex: index du DataFrame de prédiction) ou un int
    probabilite_depart: float = Field(
        ...,  # Requis
        ge=0.0,
        le=1.0,  # Ajout de contraintes de validation (>=0 et <=1)
        json_schema_extra={"example": 0.65},
        description="Probabilité que l'employé quitte l'entreprise (entre 0.0 et 1.0).",
    )
    prediction_depart: int = Field(
        ...,  # Requis
        json_schema_extra={"example": 1},
        description="Prédiction de départ (0 pour 'Reste', 1 pour 'Part').",
    )


class BulkPredictionInput(BaseModel):
    """
    Schéma Pydantic pour les requêtes de prédiction en masse.
    Attend une liste d'objets EmployeeInput.
    """

    employees: List[EmployeeInput]


class BulkPredictionOutput(BaseModel):
    """
    Schéma Pydantic pour la réponse des prédictions en masse.
    Retourne une liste d'objets PredictionOutput.
    """

    predictions: List[PredictionOutput]
