from fastapi.testclient import TestClient
from src.api.main import app # Importez votre application FastAPI
from src.api.schemas import EmployeeInput # Pour créer des données d'exemple
import pandas as pd
from unittest.mock import patch # Pour mocker la fonction de prédiction

# Initialiser le TestClient
client = TestClient(app)

# Mocker la fonction predict_attrition pour ne pas dépendre du modèle réel
# pendant les tests unitaires de l'API.
# Vous pouvez aussi choisir de tester la pipeline complète (test d'intégration).
MOCK_PREDICTION_OUTPUT = [
    {
        "id_employe": "EMP_TEST_1",
        "probabilite_depart": 0.75,
        "prediction_depart": 1
    }
]

# Données d'exemple valides (doivent correspondre à votre schéma EmployeeInput)
# Reprenez l'exemple de votre schéma EmployeeInput
VALID_EMPLOYEE_DATA = {
    'age': 45,
    'genre': 'M',
    'revenu_mensuel': 4850,
    'statut_marital': 'Célibataire',
    'departement': 'Commercial',
    'poste': 'Cadre Commercial',
    'nombre_experiences_precedentes': 8,
    'annees_dans_l_entreprise': 5,
    'satisfaction_employee_environnement': 4,
    'note_evaluation_precedente': 3,
    'satisfaction_employee_nature_travail': 3,
    'satisfaction_employee_equipe': 3,
    'satisfaction_employee_equilibre_pro_perso': 3,
    'note_evaluation_actuelle': 3,
    'heure_supplementaires': 'Oui',
    'augementation_salaire_precedente': '15 %',
    'nombre_participation_pee': 0,
    'nb_formations_suivies': 3,
    'distance_domicile_travail': 20,
    'niveau_education': 3,
    'domaine_etude': 'Infra & Cloud',
    'frequence_deplacement': 'Occasionnel',
    'annees_depuis_la_derniere_promotion': 0
}

def test_read_root():
    """Teste l'endpoint racine /."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de Prédiction d'Attrition RH - v0.1.0. Accédez à /docs pour la documentation."} # Adaptez

@patch("src.api.main.predict_attrition", return_value=MOCK_PREDICTION_OUTPUT)
def test_predict_single_valid_data(mock_predict):
    """Teste /predict avec des données valides."""
    response = client.post("/predict", json=VALID_EMPLOYEE_DATA)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["prediction_depart"] == MOCK_PREDICTION_OUTPUT[0]["prediction_depart"]
    assert "probabilite_depart" in json_response
    # Vérifier que predict_attrition a été appelé avec les bonnes données
    mock_predict.assert_called_once()
    # Vous pouvez vérifier plus en détail l'argument de mock_predict si besoin

def test_predict_single_invalid_data_missing_field():
    """Teste /predict avec un champ requis manquant."""
    invalid_data = VALID_EMPLOYEE_DATA.copy()
    del invalid_data["age"] # 'age' est un champ requis
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422 # Unprocessable Entity

def test_predict_single_invalid_data_wrong_type():
    """Teste /predict avec un type de données incorrect."""
    invalid_data = VALID_EMPLOYEE_DATA.copy()
    invalid_data["age"] = "quarante-deux" # 'age' doit être un int
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422

@patch("src.api.main.predict_attrition", return_value=MOCK_PREDICTION_OUTPUT * 2) # Simule une réponse pour 2 employés
def test_predict_bulk_valid_data(mock_predict_bulk):
    """Teste /predict_bulk avec des données valides."""
    bulk_data = {"employees": [VALID_EMPLOYEE_DATA, VALID_EMPLOYEE_DATA]}
    response = client.post("/predict_bulk", json=bulk_data)
    assert response.status_code == 200
    json_response = response.json()
    assert "predictions" in json_response
    assert len(json_response["predictions"]) == 2
    assert json_response["predictions"][0]["prediction_depart"] == MOCK_PREDICTION_OUTPUT[0]["prediction_depart"]
    mock_predict_bulk.assert_called_once()

def test_predict_bulk_empty_list():
    """Teste /predict_bulk avec une liste d'employés vide."""
    response = client.post("/predict_bulk", json={"employees": []})
    assert response.status_code == 400 # Bad Request (ou comme géré par votre API)