from fastapi import FastAPI, HTTPException, status
import pandas as pd
import logging
from typing import List

# Importe nos schémas Pydantic
from .schemas import EmployeeInput, PredictionOutput, BulkPredictionInput, BulkPredictionOutput
# Importe notre fonction de prédiction et le chargement
from src.modeling.predict import predict_attrition, load_prediction_pipeline
# Importe notre configuration
from src import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialiser l'application FastAPI
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="Une API pour prédire le risque d'attrition des employés."
)

@app.on_event("startup")
async def startup_event():
    """
    Événement exécuté au démarrage de l'API.
    Charge la pipeline de prédiction en mémoire.
    """
    logger.info("Chargement de la pipeline au démarrage...")
    pipeline = load_prediction_pipeline()
    if pipeline is None:
        logger.error("ÉCHEC du chargement de la pipeline au démarrage. L'API pourrait ne pas fonctionner.")
        # Vous pourriez vouloir empêcher le démarrage si la pipeline est cruciale,
        # mais pour l'instant, on logue juste une erreur.
    else:
        logger.info("Pipeline chargée avec succès au démarrage.")

@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Endpoint racine. Permet de vérifier rapidement si l'API est en ligne.
    """
    return {"message": f"Bienvenue sur l'{config.API_TITLE} - v{config.API_VERSION}. Accédez à /docs pour la documentation."}

@app.post("/predict", response_model=PredictionOutput, tags=["Predictions"])
async def predict_single(employee_data: EmployeeInput):
    """
    Prédit le risque d'attrition pour **un seul** employé.

    Prend en entrée un objet JSON avec les caractéristiques de l'employé.
    Retourne la probabilité de départ et la prédiction.
    """
    # Vérifier si la pipeline est chargée
    if load_prediction_pipeline() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle n'est pas chargé. Veuillez réessayer plus tard ou contacter un administrateur."
        )

    try:
        # Convertir l'input Pydantic en DataFrame Pandas (avec une seule ligne)
        # Utiliser .model_dump() pour Pydantic v2
        df = pd.DataFrame([employee_data.model_dump()], index=['SINGLE_PREDICT'])
        logger.info(f"Prédiction pour 1 employé : {employee_data.model_dump(exclude_none=True)}") # Log sans les None

        # Faire la prédiction
        results = predict_attrition(df)

        # Gérer les erreurs de prédiction
        if isinstance(results, dict) and "error" in results:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=results["error"])

        if not results:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="La prédiction a échoué sans message d'erreur spécifique.")

        # Retourner le premier (et unique) résultat
        return results[0]

    except Exception as e:
        logger.error(f"Erreur dans /predict : {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne : {e}")

@app.post("/predict_bulk", response_model=BulkPredictionOutput, tags=["Predictions"])
async def predict_bulk(input_data: BulkPredictionInput):
    """
    Prédit le risque d'attrition pour **plusieurs** employés.

    Prend en entrée un objet JSON contenant une liste ('employees')
    d'objets avec les caractéristiques des employés.
    Retourne une liste de prédictions.
    """
    if load_prediction_pipeline() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle n'est pas chargé."
        )

    if not input_data.employees:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La liste d'employés est vide.")

    try:
        # Convertir la liste d'inputs Pydantic en DataFrame Pandas
        employee_list = [emp.model_dump() for emp in input_data.employees]
        df = pd.DataFrame(employee_list, index=[f"BULK_{i}" for i in range(len(employee_list))])
        logger.info(f"Prédiction pour {len(df)} employés.")

        # Faire la prédiction
        results = predict_attrition(df)

        if isinstance(results, dict) and "error" in results:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=results["error"])

        if not results:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="La prédiction en masse a échoué.")

        return {"predictions": results}

    except Exception as e:
        logger.error(f"Erreur dans /predict_bulk : {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne : {e}")

# Si vous voulez lancer directement ce fichier (pour des tests rapides,
# bien que 'uvicorn' soit la méthode standard)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)