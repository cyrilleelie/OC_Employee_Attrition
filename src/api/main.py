from fastapi import FastAPI, HTTPException, status, Depends # AJOUT: Depends
import pandas as pd
import logging
from typing import List
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session # AJOUT: Session

# Importe nos schémas Pydantic
from .schemas import EmployeeInput, PredictionOutput, BulkPredictionInput, BulkPredictionOutput
# Importe notre fonction de prédiction et le chargement
from src.modeling.predict import predict_attrition, load_prediction_pipeline
# Importe notre configuration
from src import config
# AJOUT: Imports pour la base de données
from src.database.database_setup import get_db, SessionLocal # Assurez-vous que get_db est bien ici
from src.database.models import ApiPredictionLog # Notre modèle SQLAlchemy pour les logs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Chargement de la pipeline au démarrage (via lifespan)...")
    pipeline = load_prediction_pipeline()
    if pipeline is None:
        logger.error("ÉCHEC du chargement de la pipeline au démarrage. L'API pourrait ne pas fonctionner.")
    else:
        logger.info("Pipeline chargée avec succès au démarrage.")
    yield
    logger.info("Application API en cours d'arrêt.")

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="Une API pour prédire le risque d'attrition des employés.",
    lifespan=lifespan
)

@app.get("/", tags=["Health Check"])
async def read_root():
    return {"message": f"Bienvenue sur l'{config.API_TITLE} - v{config.API_VERSION}. Accédez à /docs pour la documentation."}

@app.post("/predict", response_model=PredictionOutput, tags=["Predictions"])
async def predict_single(
    employee_data: EmployeeInput, # Les données brutes de l'employé
    db: Session = Depends(get_db) # Injection de la session BDD
):
    if load_prediction_pipeline() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le modèle n'est pas chargé."
        )
    try:
        # Convertir l'input Pydantic en DataFrame Pandas pour la fonction de prédiction
        # L'index ici est arbitraire car predict_attrition utilise l'index du DataFrame
        # pour le champ 'id_employe' dans sa sortie. On pourrait vouloir passer
        # un 'employee_id' optionnel dans EmployeeInput et l'utiliser ici si disponible.
        # Pour l'instant, on utilise un index par défaut.
        temp_index_for_df = "API_SINGLE_PREDICT" # Ou un UUID, ou un ID passé dans employee_data
        df = pd.DataFrame([employee_data.model_dump()], index=[temp_index_for_df])
        
        logger.info(f"Prédiction pour 1 employé (données brutes): {employee_data.model_dump(exclude_none=True)}")
        
        prediction_results_list = predict_attrition(df) # Devrait retourner une liste avec un seul dict

        if isinstance(prediction_results_list, dict) and "error" in prediction_results_list:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=prediction_results_list["error"])
        if not prediction_results_list or len(prediction_results_list) == 0:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="La prédiction a échoué.")

        single_prediction_result = prediction_results_list[0]

        # --- Enregistrement dans la base de données ---
        try:
            log_entry = ApiPredictionLog(
                # employee_id_concerne: si EmployeeInput avait un champ id, on l'utiliserait ici.
                # Sinon, on peut utiliser l'index que predict_attrition a retourné, s'il est significatif.
                # Pour cet exemple, on va supposer qu'on loggue l'ID généré/utilisé par predict_attrition,
                # ou un ID passé dans l'input si vous l'ajoutez à EmployeeInput
                employee_id_concerne=str(single_prediction_result.get("id_employe", temp_index_for_df)),
                input_data=employee_data.model_dump(), # Stocke le dictionnaire Pydantic
                prediction_probabilite=single_prediction_result["probabilite_depart"],
                prediction_classe=single_prediction_result["prediction_depart"],
                version_modele=config.MODEL_NAME # Ou une version plus dynamique si vous en avez
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry) # Pour obtenir log_id si besoin
            logger.info(f"Prédiction enregistrée dans la BDD avec log_id: {log_entry.log_id}")
        except Exception as db_error:
            logger.error(f"Erreur lors de l'enregistrement du log en BDD: {db_error}", exc_info=True)
            db.rollback()
            # On ne veut pas que l'appel API échoue si seul le logging échoue
            # Mais c'est un choix de conception. Vous pourriez vouloir lever une erreur ici.
        # --- Fin Enregistrement ---

        return single_prediction_result

    except HTTPException as http_exc: # Repropager les HTTPException
        raise http_exc
    except Exception as e:
        logger.error(f"Erreur dans /predict : {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne : {e}")

@app.post("/predict_bulk", response_model=BulkPredictionOutput, tags=["Predictions"])
async def predict_bulk(
    input_data: BulkPredictionInput,
    db: Session = Depends(get_db) # Injection de la session BDD
):
    if load_prediction_pipeline() is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Le modèle n'est pas chargé.")
    if not input_data.employees:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La liste d'employés est vide.")

    try:
        # Conserver les inputs originaux pour le logging
        original_inputs = [emp.model_dump() for emp in input_data.employees]
        
        # Créer le DataFrame pour la prédiction
        df_index = [f"BULK_{i}" for i in range(len(original_inputs))] # Index temporaires pour le DF
        df = pd.DataFrame(original_inputs, index=df_index)
        logger.info(f"Prédiction en masse pour {len(df)} employés.")
        
        prediction_results_list = predict_attrition(df) # Ceci est une liste de dictionnaires

        if isinstance(prediction_results_list, dict) and "error" in prediction_results_list:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=prediction_results_list["error"])
        if not prediction_results_list or len(prediction_results_list) != len(original_inputs):
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="La prédiction en masse a échoué ou n'a pas retourné le bon nombre de résultats.")

        # --- Enregistrement dans la base de données ---
        try:
            for i, original_input_dict in enumerate(original_inputs):
                current_prediction_result = prediction_results_list[i]
                log_entry = ApiPredictionLog(
                    employee_id_concerne=str(current_prediction_result.get("id_employe", df_index[i])),
                    input_data=original_input_dict,
                    prediction_probabilite=current_prediction_result["probabilite_depart"],
                    prediction_classe=current_prediction_result["prediction_depart"],
                    version_modele=config.MODEL_NAME
                )
                db.add(log_entry)
            db.commit()
            logger.info(f"{len(original_inputs)} prédictions en masse enregistrées dans la BDD.")
        except Exception as db_error:
            logger.error(f"Erreur lors de l'enregistrement des logs en masse en BDD: {db_error}", exc_info=True)
            db.rollback()
        # --- Fin Enregistrement ---

        return {"predictions": prediction_results_list}

    except HTTPException as http_exc: # Repropager les HTTPException
        raise http_exc
    except Exception as e:
        logger.error(f"Erreur dans /predict_bulk : {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne : {e}")