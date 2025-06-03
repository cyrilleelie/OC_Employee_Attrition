"""
Module principal de l'API FastAPI pour la prédiction d'attrition des employés.

Définit les endpoints de l'API, gère le cycle de vie de l'application (chargement du modèle), valide les données d'entrée, appelle la logique de prédiction, et enregistre les interactions dans une base de données PostgreSQL.
"""

from fastapi import FastAPI, HTTPException, status, Depends
import pandas as pd
import logging
from contextlib import (
    asynccontextmanager,
)  # Pour le gestionnaire de cycle de vie (lifespan)
from sqlalchemy.orm import Session  # Pour l'injection de dépendance de la session BDD

# Importe les schémas Pydantic pour la validation et la sérialisation des données
from .schemas import (
    EmployeeInput,
    PredictionOutput,
    BulkPredictionInput,
    BulkPredictionOutput,
)

# Importe la logique de prédiction et de chargement du modèle
from src.modeling.predict import predict_attrition, load_prediction_pipeline

# Importe les configurations globales du projet
from src import config

# Imports pour l'interaction avec la base de données
from src.database.database_setup import get_db  # Dépendance pour la session BDD
from src.database.models import (
    ApiPredictionLog,
)  # Modèle SQLAlchemy pour les logs de prédiction

# Configuration de base du logging pour ce module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie (lifespan) pour l'application FastAPI.

    Est exécuté au démarrage et à l'arrêt de l'application.
    Utilisé ici pour charger la pipeline de prédiction au démarrage.
    """
    logger.info(
        "Démarrage de l'application API : Tentative de chargement de la pipeline de prédiction..."
    )
    pipeline = (
        load_prediction_pipeline()
    )  # Tente de charger la pipeline stockée globalement dans predict.py
    if pipeline is None:
        logger.error(
            "ÉCHEC CRITIQUE du chargement de la pipeline au démarrage. "
            "L'API pourrait ne pas être en mesure de faire des prédictions."
        )
    else:
        logger.info("Pipeline de prédiction chargée avec succès au démarrage.")
    yield  # L'application s'exécute ici
    logger.info("Arrêt de l'application API.")


# Initialisation de l'application FastAPI avec le gestionnaire de cycle de vie
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="Une API pour prédire le risque d'attrition des employés, avec enregistrement des prédictions.",
    lifespan=lifespan,
)


@app.get("/", tags=["Health Check"], summary="Vérification de l'état de l'API")
async def read_root():
    """
    Endpoint racine pour vérifier la disponibilité et la version de l'API.
    """
    return {
        "message": f"Bienvenue sur l'{config.API_TITLE} - v{config.API_VERSION}. Accédez à /docs pour la documentation interactive."
    }


@app.post(
    "/predict",
    response_model=PredictionOutput,
    tags=["Predictions"],
    summary="Prédire l'attrition pour un seul employé",
)
async def predict_single(
    employee_data: EmployeeInput,  # Données d'entrée validées par Pydantic
    db: Session = Depends(get_db),  # Injection de la session de base de données
):
    """
    Prédit le risque d'attrition pour un seul employé.

    Les données de l'employé sont fournies dans le corps de la requête au format JSON.
    La prédiction (probabilité et classe) est retournée.
    L'input et l'output de la prédiction sont enregistrés en base de données.
    """
    if load_prediction_pipeline() is None:  # Vérifie si la pipeline globale est chargée
        logger.error(
            "Tentative d'appel à /predict alors que la pipeline n'est pas chargée."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle de prédiction non disponible. Veuillez réessayer plus tard.",
        )
    try:
        # L'index est utilisé par predict_attrition pour le champ 'id_employe' de la sortie.
        # Un identifiant unique pour cette requête serait idéal.
        temp_index_for_df = "PREDICT_SINGLE_REQUEST"  # Pourrait être un UUID généré

        # Conversion des données Pydantic en DataFrame Pandas pour la fonction de prédiction
        df = pd.DataFrame([employee_data.model_dump()], index=[temp_index_for_df])

        logger.info(
            f"Requête /predict reçue pour l'employé (index temporaire: {temp_index_for_df}). "
            f"Données : {employee_data.model_dump(exclude_none=True)}"
        )

        # Appel à la logique de prédiction
        prediction_results_list = predict_attrition(df)

        # Gestion des erreurs retournées par predict_attrition
        if (
            isinstance(prediction_results_list, dict)
            and "error" in prediction_results_list
        ):
            logger.error(
                f"Erreur retournée par predict_attrition: {prediction_results_list['error']}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=prediction_results_list["error"],
            )
        if not prediction_results_list:  # Devrait être une liste d'un élément
            logger.error(
                "predict_attrition n'a retourné aucun résultat pour une prédiction unique."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La prédiction a échoué à produire un résultat.",
            )

        single_prediction_result = prediction_results_list[0]

        # Enregistrement en base de données
        if config.ENABLE_API_DB_LOGGING:  # Utilisation de la variable de configuration
            try:
                print("DEBUG: Entrée dans le bloc de logging BDD")  # DEBUG
                log_entry = ApiPredictionLog(
                    employee_id_concerne=str(
                        single_prediction_result.get("id_employe", temp_index_for_df)
                    ),
                    input_data=employee_data.model_dump(),  # Stocke le dictionnaire complet des données d'entrée
                    prediction_probabilite=single_prediction_result[
                        "probabilite_depart"
                    ],
                    prediction_classe=single_prediction_result["prediction_depart"],
                    version_modele=config.MODEL_NAME,
                )
                print(f"DEBUG: log_entry créé: {log_entry}")  # DEBUG
                db.add(log_entry)  # db est la session ici
                print("DEBUG: db.add(log_entry) appelé")  # DEBUG
                db.commit()
                db.refresh(log_entry)
                logger.info(
                    f"Prédiction pour {temp_index_for_df} enregistrée en BDD (log_id: {log_entry.log_id})."
                )
            except Exception as db_error:
                logger.error(
                    f"Erreur lors de l'enregistrement du log de prédiction en BDD: {db_error}",
                    exc_info=True,
                )
                db.rollback()
                # Pas de HTTPException ici pour ne pas faire échouer la réponse au client si seul le log échoue.

        return single_prediction_result

    except (
        HTTPException
    ) as http_exc:  # Important de repropager les HTTPException pour que FastAPI les gère
        raise http_exc
    except Exception as e:  # Capture les autres exceptions non prévues
        logger.error(f"Erreur inattendue dans l'endpoint /predict : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite lors du traitement de votre requête.",
        )


@app.post(
    "/predict_bulk",
    response_model=BulkPredictionOutput,
    tags=["Predictions"],
    summary="Prédire l'attrition pour plusieurs employés",
)
async def predict_bulk(
    input_data: BulkPredictionInput,  # Données d'entrée validées (liste d'employés)
    db: Session = Depends(get_db),  # Injection de la session BDD
):
    """
    Prédit le risque d'attrition pour une liste d'employés.

    Les données des employés sont fournies dans le corps de la requête au format JSON,
    sous une clé "employees" contenant une liste d'objets employé.
    Retourne une liste de prédictions.
    Les inputs et outputs de chaque prédiction sont enregistrés en base de données.
    """
    if load_prediction_pipeline() is None:
        logger.error(
            "Tentative d'appel à /predict_bulk alors que la pipeline n'est pas chargée."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle de prédiction non disponible. Veuillez réessayer plus tard.",
        )
    if (
        not input_data.employees
    ):  # input_data est BulkPredictionInput, input_data.employees est la liste
        logger.warning("Requête /predict_bulk reçue avec une liste d'employés vide.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # Erreur client
            detail="La liste d'employés ('employees') ne peut pas être vide.",
        )

    try:
        original_inputs = [emp.model_dump() for emp in input_data.employees]

        # Création d'index temporaires pour le DataFrame, utiles pour le retour de predict_attrition
        df_indices = [f"BULK_REQ_{i}" for i in range(len(original_inputs))]
        df_for_prediction = pd.DataFrame(original_inputs, index=df_indices)

        logger.info(
            f"Requête /predict_bulk reçue pour {len(df_for_prediction)} employés."
        )

        prediction_results_list = predict_attrition(df_for_prediction)

        if (
            isinstance(prediction_results_list, dict)
            and "error" in prediction_results_list
        ):
            logger.error(
                f"Erreur retournée par predict_attrition pour une requête en masse: {prediction_results_list['error']}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=prediction_results_list["error"],
            )
        if not prediction_results_list or len(prediction_results_list) != len(
            original_inputs
        ):
            logger.error(
                "predict_attrition n'a pas retourné le bon nombre de résultats pour une requête en masse."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La prédiction en masse a échoué ou un nombre incorrect de résultats a été retourné.",
            )

        # Enregistrement en base de données
        if config.ENABLE_API_DB_LOGGING:
            log_entries_to_add = []
            try:
                for i, original_input_dict in enumerate(original_inputs):
                    current_prediction_result = prediction_results_list[i]
                    log_entry = ApiPredictionLog(
                        employee_id_concerne=str(
                            current_prediction_result.get("id_employe", df_indices[i])
                        ),
                        input_data=original_input_dict,
                        prediction_probabilite=current_prediction_result[
                            "probabilite_depart"
                        ],
                        prediction_classe=current_prediction_result[
                            "prediction_depart"
                        ],
                        version_modele=config.MODEL_NAME,
                    )
                    log_entries_to_add.append(log_entry)

                db.add_all(
                    log_entries_to_add
                )  # Plus efficace pour les insertions multiples
                db.commit()
                logger.info(
                    f"{len(original_inputs)} prédictions en masse enregistrées en BDD."
                )
            except Exception as db_error:
                logger.error(
                    f"Erreur lors de l'enregistrement des logs de prédiction en masse en BDD: {db_error}",
                    exc_info=True,
                )
                db.rollback()

        return {"predictions": prediction_results_list}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(
            f"Erreur inattendue dans l'endpoint /predict_bulk : {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite lors du traitement de votre requête en masse.",
        )
