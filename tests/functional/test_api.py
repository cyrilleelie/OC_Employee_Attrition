from fastapi.testclient import TestClient
from src.api.main import app  # Importez votre application FastAPI
from unittest.mock import patch, MagicMock  # Pour mocker la fonction de prédiction

# Importe les configurations globales du projet
from src import config

# Initialiser le TestClient
client = TestClient(app)

# Mocker la fonction predict_attrition pour ne pas dépendre du modèle réel
# pendant les tests unitaires de l'API.
# Vous pouvez aussi choisir de tester la pipeline complète (test d'intégration).
MOCK_PREDICTION_OUTPUT = [
    {"id_employe": "EMP_TEST_1", "probabilite_depart": 0.75, "prediction_depart": 1}
]

# Données d'exemple valides (doivent correspondre à votre schéma EmployeeInput)
# Reprenez l'exemple de votre schéma EmployeeInput
VALID_EMPLOYEE_DATA = {
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


def test_read_root():
    """Teste l'endpoint racine /."""
    response = client.get("/")
    assert response.status_code == 200
    expected_message = f"Bienvenue sur l'{config.API_TITLE} - v{config.API_VERSION}. Accédez à /docs pour la documentation interactive."
    assert response.json() == {"message": expected_message}


@patch("src.api.main.predict_attrition", return_value=MOCK_PREDICTION_OUTPUT)
def test_predict_single_valid_data(mock_predict):
    """Teste /predict avec des données valides."""
    response = client.post("/predict", json=VALID_EMPLOYEE_DATA)
    assert response.status_code == 200
    json_response = response.json()
    assert (
        json_response["prediction_depart"]
        == MOCK_PREDICTION_OUTPUT[0]["prediction_depart"]
    )
    assert "probabilite_depart" in json_response
    # Vérifier que predict_attrition a été appelé avec les bonnes données
    mock_predict.assert_called_once()
    # Vous pouvez vérifier plus en détail l'argument de mock_predict si besoin


def test_predict_single_invalid_data_missing_field():
    """Teste /predict avec un champ requis manquant."""
    invalid_data = VALID_EMPLOYEE_DATA.copy()
    del invalid_data["age"]  # 'age' est un champ requis
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity


def test_predict_single_invalid_data_wrong_type():
    """Teste /predict avec un type de données incorrect."""
    invalid_data = VALID_EMPLOYEE_DATA.copy()
    invalid_data["age"] = "quarante-deux"  # 'age' doit être un int
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


@patch(
    "src.api.main.predict_attrition", return_value=MOCK_PREDICTION_OUTPUT * 2
)  # Simule une réponse pour 2 employés
def test_predict_bulk_valid_data(mock_predict_bulk):
    """Teste /predict_bulk avec des données valides."""
    bulk_data = {"employees": [VALID_EMPLOYEE_DATA, VALID_EMPLOYEE_DATA]}
    response = client.post("/predict_bulk", json=bulk_data)
    assert response.status_code == 200
    json_response = response.json()
    assert "predictions" in json_response
    assert len(json_response["predictions"]) == 2
    assert (
        json_response["predictions"][0]["prediction_depart"]
        == MOCK_PREDICTION_OUTPUT[0]["prediction_depart"]
    )
    mock_predict_bulk.assert_called_once()


def test_predict_bulk_empty_list():
    """Teste /predict_bulk avec une liste d'employés vide."""
    response = client.post("/predict_bulk", json={"employees": []})
    assert response.status_code == 400  # Bad Request (ou comme géré par votre API)


@patch(
    "src.api.main.load_prediction_pipeline", return_value=None
)  # Simule un échec de chargement du modèle
def test_predict_single_model_not_loaded_api(mock_load_pipeline):
    """Teste POST /predict lorsque le modèle n'est pas chargé (simulé)."""
    response = client.post("/predict", json=VALID_EMPLOYEE_DATA)
    assert response.status_code == 503  # Service Unavailable
    assert response.json() == {
        "detail": "Modèle de prédiction non disponible. Veuillez réessayer plus tard."
    }


@patch(
    "src.api.main.load_prediction_pipeline", return_value=MagicMock()
)  # Assurer que la pipeline semble chargée
@patch(
    "src.api.main.predict_attrition",
    return_value={"error": "Erreur interne de prédiction simulée"},
)
def test_predict_single_error_from_predict_attrition(mock_predict, mock_load_pipeline):
    """Teste /predict quand predict_attrition retourne une erreur."""
    response = client.post("/predict", json=VALID_EMPLOYEE_DATA)
    assert response.status_code == 500
    assert response.json() == {"detail": "Erreur interne de prédiction simulée"}
    mock_predict.assert_called_once()


@patch("src.api.main.load_prediction_pipeline", return_value=MagicMock())
@patch(
    "src.api.main.predict_attrition", return_value=[]
)  # predict_attrition retourne une liste vide
def test_predict_single_empty_list_from_predict_attrition(
    mock_predict, mock_load_pipeline
):
    """Teste /predict quand predict_attrition retourne une liste vide (inattendu)."""
    response = client.post("/predict", json=VALID_EMPLOYEE_DATA)
    assert response.status_code == 500
    assert response.json() == {
        "detail": "La prédiction a échoué à produire un résultat."
    }
    mock_predict.assert_called_once()


# Tests similaires pour /predict_bulk
@patch("src.api.main.load_prediction_pipeline", return_value=MagicMock())
@patch("src.api.main.predict_attrition", return_value={"error": "Erreur bulk simulée"})
def test_predict_bulk_error_from_predict_attrition(
    mock_predict_bulk, mock_load_pipeline
):
    """Teste /predict_bulk quand predict_attrition retourne une erreur."""
    bulk_data = {"employees": [VALID_EMPLOYEE_DATA]}
    response = client.post("/predict_bulk", json=bulk_data)
    assert response.status_code == 500
    assert response.json() == {"detail": "Erreur bulk simulée"}
    mock_predict_bulk.assert_called_once()


@patch("src.api.main.load_prediction_pipeline", return_value=MagicMock())
@patch(
    "src.api.main.predict_attrition", return_value=[MOCK_PREDICTION_OUTPUT[0]]
)  # Retourne 1 résultat au lieu de 2
def test_predict_bulk_wrong_results_count_from_predict_attrition(
    mock_predict_bulk, mock_load_pipeline
):
    """Teste /predict_bulk quand predict_attrition ne retourne pas le bon nombre de résultats."""
    bulk_data = {
        "employees": [VALID_EMPLOYEE_DATA, VALID_EMPLOYEE_DATA]
    }  # Attend 2 résultats
    response = client.post("/predict_bulk", json=bulk_data)
    assert response.status_code == 500
    assert response.json() == {
        "detail": "La prédiction en masse a échoué ou un nombre incorrect de résultats a été retourné."
    }
    mock_predict_bulk.assert_called_once()


def test_predict_single_invalid_enum_value_genre():
    """Teste /predict avec une valeur non autorisée pour un champ Enum (genre)."""
    invalid_data = VALID_EMPLOYEE_DATA.copy()
    invalid_data["genre"] = (
        "Autre"  # Supposons que "Autre" n'est pas dans votre Enum/liste autorisée
    )

    response = client.post("/predict", json=invalid_data)
    assert (
        response.status_code == 422
    )  # Pydantic devrait lever une erreur de validation
    json_response = response.json()
    assert "detail" in json_response
    # Vérifier que le message d'erreur mentionne 'genre'
    error_found = False
    for error in json_response.get("detail", []):
        if "genre" in error.get("loc", []):
            error_found = True
            break
    assert (
        error_found
    ), "Le message d'erreur de validation ne mentionne pas le champ 'genre'."
