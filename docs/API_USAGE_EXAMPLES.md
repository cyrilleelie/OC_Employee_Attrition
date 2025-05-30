# Exemples d'Utilisation de l'API de Prédiction d'Attrition RH

Ce document fournit des exemples concrets pour interagir avec l'API de prédiction d'attrition des employés. Pour que ces exemples fonctionnent, assurez-vous que l'API est en cours d'exécution (par exemple, localement sur `http://127.0.0.1:8000` ou sur son URL de déploiement sur Hugging Face Spaces).

La documentation interactive complète de l'API (Swagger UI), générée automatiquement par FastAPI, est toujours disponible à l'endpoint `/docs` de l'API en cours d'exécution (par exemple, `http://127.0.0.1:8000/docs`).

## 1. Utilisation avec `curl`

`curl` est un outil en ligne de commande polyvalent pour transférer des données avec des URL. Il est disponible sur la plupart des systèmes Linux et macOS, et peut être installé sur Windows.

### Endpoint Racine (`GET /`)

Cet endpoint permet de vérifier si l'API est en ligne et d'obtenir un message de bienvenue.

**Commande :**
```bash
curl -X GET "[http://127.0.0.1:8000/](http://127.0.0.1:8000/)"
```

**Réponse Attendue (exemple) :**
```json
{
  "message": "Bienvenue sur l'API Prédiction Attrition RH - v0.1.0. Accédez à /docs pour la documentation."
}
```

### Endpoint Prédiction Unique (`POST /predict`)

Cet endpoint permet d'obtenir une prédiction pour un seul employé. Le corps de la requête doit être un objet JSON correspondant au schéma `EmployeeInput`.

**Commande :**
```bash
curl -X POST "[http://127.0.0.1:8000/predict](http://127.0.0.1:8000/predict)" \
-H "Content-Type: application/json" \
-d '{
  "age": 45,
  "annees_dans_l_entreprise": 5,
  "annees_depuis_la_derniere_promotion": 0,
  "augementation_salaire_precedente": "15 %",
  "departement": "Commercial",
  "distance_domicile_travail": 20,
  "domaine_etude": "Infra & Cloud",
  "frequence_deplacement": "Occasionnel",
  "genre": "M",
  "heure_supplementaires": "Oui",
  "nb_formations_suivies": 3,
  "niveau_education": 3,
  "nombre_experiences_precedentes": 8,
  "nombre_participation_pee": 0,
  "note_evaluation_actuelle": 3,
  "note_evaluation_precedente": 3,
  "poste": "Cadre Commercial",
  "revenu_mensuel": 4850,
  "satisfaction_employee_environnement": 4,
  "satisfaction_employee_equilibre_pro_perso": 3,
  "satisfaction_employee_equipe": 3,
  "satisfaction_employee_nature_travail": 3,
  "statut_marital": "Célibataire"
}'
```

**Réponse Attendue (structure) :**
```json
{
  "id_employe": "API_SINGLE_PREDICT", // L'ID peut varier basé sur l'index interne
  "probabilite_depart": 0.123,       // Valeur d'exemple
  "prediction_depart": 0              // Valeur d'exemple
}
```

### Endpoint Prédiction en Masse (`POST /predict_bulk`)

Cet endpoint permet d'obtenir des prédictions pour plusieurs employés en un seul appel. Le corps de la requête est un objet JSON contenant une clé `"employees"` dont la valeur est une liste d'objets `EmployeeInput`.

**Commande :**
```bash
curl -X POST "[http://127.0.0.1:8000/predict_bulk](http://127.0.0.1:8000/predict_bulk)" \
-H "Content-Type: application/json" \
-d '{
  "employees": [
    {
        "age": 45,
        "annees_dans_l_entreprise": 5,
        "annees_depuis_la_derniere_promotion": 0,
        "augementation_salaire_precedente": "15 %",
        "departement": "Commercial",
        "distance_domicile_travail": 20,
        "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel",
        "genre": "M",
        "heure_supplementaires": "Oui",
        "nb_formations_suivies": 3,
        "niveau_education": 3,
        "nombre_experiences_precedentes": 8,
        "nombre_participation_pee": 0,
        "note_evaluation_actuelle": 3,
        "note_evaluation_precedente": 3,
        "poste": "Cadre Commercial",
        "revenu_mensuel": 4850,
        "satisfaction_employee_environnement": 4,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_nature_travail": 3,
        "statut_marital": "Célibataire"
    },
    {
        "age": 45,
        "annees_dans_l_entreprise": 5,
        "annees_depuis_la_derniere_promotion": 0,
        "augementation_salaire_precedente": "15 %",
        "departement": "Commercial",
        "distance_domicile_travail": 20,
        "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel",
        "genre": "M",
        "heure_supplementaires": "Oui",
        "nb_formations_suivies": 3,
        "niveau_education": 3,
        "nombre_experiences_precedentes": 8,
        "nombre_participation_pee": 0,
        "note_evaluation_actuelle": 3,
        "note_evaluation_precedente": 3,
        "poste": "Cadre Commercial",
        "revenu_mensuel": 4850,
        "satisfaction_employee_environnement": 4,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_nature_travail": 3,
        "statut_marital": "Célibataire"
    }
  ]
}'
```

**Réponse Attendue (structure) :**
```json
{
  "predictions": [
    {
      "id_employe": "BULK_0",
      "probabilite_depart": 0.123, // Valeur d'exemple
      "prediction_depart": 0       // Valeur d'exemple
    },
    {
      "id_employe": "BULK_1",
      "probabilite_depart": 0.789, // Valeur d'exemple
      "prediction_depart": 1       // Valeur d'exemple
    }
  ]
}
```

## 2. Utilisation avec Python et la librairie `requests`

La librairie `requests` est la manière standard et conviviale d'interagir avec des API HTTP en Python.

### Installation :

Si vous ne l'avez pas dans votre environnement, vous pouvez l'installer avec pip :
```bash
pip install requests
```
Si vous utilisez Poetry pour un projet client séparé, ajoutez-la avec `poetry add requests`.

**Script Python d'Exemple :**
```python
import requests
import json # Utilisé pour un affichage formaté de la réponse ou pour le débogage

# URL de base de votre API (adaptez si déployée ailleurs)
BASE_URL = "[http://127.0.0.1:8000](http://127.0.0.1:8000)"

# Données d'exemple pour un employé (doit correspondre au schéma EmployeeInput)
# Assurez-vous que toutes les colonnes requises par votre schéma Pydantic sont présentes.
employee_data_1 = {
    "age": 45,
    "annees_dans_l_entreprise": 5,
    "annees_depuis_la_derniere_promotion": 0,
    "augementation_salaire_precedente": "15 %",
    "departement": "Commercial",
    "distance_domicile_travail": 20,
    "domaine_etude": "Infra & Cloud",
    "frequence_deplacement": "Occasionnel",
    "genre": "M",
    "heure_supplementaires": "Oui",
    "nb_formations_suivies": 3,
    "niveau_education": 3,
    "nombre_experiences_precedentes": 8,
    "nombre_participation_pee": 0,
    "note_evaluation_actuelle": 3,
    "note_evaluation_precedente": 3,
    "poste": "Cadre Commercial",
    "revenu_mensuel": 4850,
    "satisfaction_employee_environnement": 4,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_nature_travail": 3,
    "statut_marital": "Célibataire"
    }

employee_data_2 = {
    "age": 45,
    "annees_dans_l_entreprise": 5,
    "annees_depuis_la_derniere_promotion": 0,
    "augementation_salaire_precedente": "15 %",
    "departement": "Commercial",
    "distance_domicile_travail": 20,
    "domaine_etude": "Infra & Cloud",
    "frequence_deplacement": "Occasionnel",
    "genre": "M",
    "heure_supplementaires": "Oui",
    "nb_formations_suivies": 3,
    "niveau_education": 3,
    "nombre_experiences_precedentes": 8,
    "nombre_participation_pee": 0,
    "note_evaluation_actuelle": 3,
    "note_evaluation_precedente": 3,
    "poste": "Cadre Commercial",
    "revenu_mensuel": 4850,
    "satisfaction_employee_environnement": 4,
    "satisfaction_employee_equilibre_pro_perso": 3,
    "satisfaction_employee_equipe": 3,
    "satisfaction_employee_nature_travail": 3,
    "statut_marital": "Célibataire"
    }

def test_api_endpoints():
    # 1. Tester l'endpoint racine
    try:
        response_root = requests.get(f"{BASE_URL}/")
        response_root.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
        print("Réponse de GET /:")
        print(json.dumps(response_root.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à GET /: {e}")

    print("\n" + "-" * 50 + "\n")

    # 2. Tester l'endpoint /predict
    print("Test de POST /predict...")
    try:
        response_predict = requests.post(f"{BASE_URL}/predict", json=employee_data_1)
        response_predict.raise_for_status()
        print("Réponse de POST /predict:")
        print(json.dumps(response_predict.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à POST /predict: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Détail de l'erreur du serveur: {json.dumps(e.response.json(), indent=2)}")
            except json.JSONDecodeError:
                print(f"Détail de l'erreur du serveur (non-JSON): {e.response.text}")

    print("\n" + "-" * 50 + "\n")

    # 3. Tester l'endpoint /predict_bulk
    print("Test de POST /predict_bulk...")
    bulk_payload = {"employees": [employee_data_1, employee_data_2]}
    try:
        response_bulk = requests.post(f"{BASE_URL}/predict_bulk", json=bulk_payload)
        response_bulk.raise_for_status()
        print("Réponse de POST /predict_bulk:")
        print(json.dumps(response_bulk.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à POST /predict_bulk: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Détail de l'erreur du serveur: {json.dumps(e.response.json(), indent=2)}")
            except json.JSONDecodeError:
                print(f"Détail de l'erreur du serveur (non-JSON): {e.response.text}")

if __name__ == "__main__":
    test_api_endpoints()
```

N'oubliez pas que les valeurs (`age`, `revenu_mensuel`, etc.) dans les exemples `curl` et Python sont des placeholders. Vous devrez les remplacer par des données qui ont du sens pour votre modèle et qui respectent les types définis dans votre schéma Pydantic `EmployeeInput`.