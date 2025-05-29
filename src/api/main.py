from fastapi import FastAPI, HTTPException, status
import pandas as pd
import logging
from typing import List
from contextlib import asynccontextmanager  # AJOUTÉ

from .schemas import (
    EmployeeInput,
    PredictionOutput,
    BulkPredictionInput,
    BulkPredictionOutput,
)
from src.modeling.predict import predict_attrition, load_prediction_pipeline
from src import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- MODIFIÉ : Remplacement de @app.on_event par lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code à exécuter au démarrage
    logger.info("Chargement de la pipeline au démarrage (via lifespan)...")
    pipeline = load_prediction_pipeline()
    if pipeline is None:
        logger.error(
            "ÉCHEC du chargement de la pipeline au démarrage. L'API pourrait ne pas fonctionner."
        )
    else:
        logger.info("Pipeline chargée avec succès au démarrage.")
    yield
    # Code à exécuter à l'arrêt (si besoin)
    logger.info("Application API en cours d'arrêt.")


app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="Une API pour prédire le risque d'attrition des employés.",
    lifespan=lifespan,  # AJOUTÉ : Utilisation du gestionnaire de cycle de vie
)
# --- FIN MODIFICATION ---


@app.get("/", tags=["Health Check"])
async def read_root():
    return {
        "message": f"Bienvenue sur l'{config.API_TITLE} - v{config.API_VERSION}. Accédez à /docs pour la documentation."
    }


@app.post("/predict", response_model=PredictionOutput, tags=["Predictions"])
async def predict_single(employee_data: EmployeeInput):
    if (
        load_prediction_pipeline() is None
    ):  # Vérifie si la pipeline est chargée (elle devrait l'être par lifespan)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle n'est pas chargé. Veuillez réessayer plus tard ou contacter un administrateur.",
        )
    try:
        df = pd.DataFrame([employee_data.model_dump()], index=["SINGLE_PREDICT"])
        logger.info(
            f"Prédiction pour 1 employé : {employee_data.model_dump(exclude_none=True)}"
        )
        results = predict_attrition(df)
        if isinstance(results, dict) and "error" in results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=results["error"],
            )
        if not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La prédiction a échoué sans message.",
            )
        return results[0]
    except Exception as e:
        logger.error(f"Erreur dans /predict : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e}",
        )


@app.post("/predict_bulk", response_model=BulkPredictionOutput, tags=["Predictions"])
async def predict_bulk(input_data: BulkPredictionInput):
    if load_prediction_pipeline() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle n'est pas chargé.",
        )
    if not input_data.employees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liste d'employés est vide.",
        )
    try:
        employee_list = [emp.model_dump() for emp in input_data.employees]
        df = pd.DataFrame(
            employee_list, index=[f"BULK_{i}" for i in range(len(employee_list))]
        )
        logger.info(f"Prédiction pour {len(df)} employés.")
        results = predict_attrition(df)
        if isinstance(results, dict) and "error" in results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=results["error"],
            )
        if not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La prédiction en masse a échoué.",
            )
        return {"predictions": results}
    except Exception as e:
        logger.error(f"Erreur dans /predict_bulk : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne : {e}",
        )
