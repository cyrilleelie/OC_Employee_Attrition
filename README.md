---
title: API Prédiction Attrition RH
emoji: 📊
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
license: mit # Ou apache-2.0, etc. - Mettez la licence que vous souhaitez
---

# Projet : Prédiction de l'Attrition des Employés et API

Ce projet a pour objectif d'analyser les données RH afin de construire un modèle de Machine Learning capable de prédire le départ volontaire (attrition) des employés. Le modèle est ensuite exposé via une API RESTful construite avec FastAPI, prête à être déployée, et les interactions avec l'API sont enregistrées dans une base de données PostgreSQL.

## 🎯 Objectifs

* **Analyser** les facteurs clés influençant l'attrition des employés.
* **Construire et Entraîner** un modèle de classification binaire performant.
* **Développer une API** pour obtenir des prédictions en temps réel pour un ou plusieurs employés.
* **Intégrer une base de données PostgreSQL** pour la gestion des données d'entraînement et l'enregistrement des prédictions de l'API.
* **Conteneuriser** l'application avec Docker pour un déploiement facile de l'API.
* **Déployer** l'API sur Hugging Face Spaces.

## 🛠️ Technologies Utilisées

* **Langage :** Python 3.12
* **Analyse & ML :** Pandas, NumPy, Scikit-learn, Joblib
* **API :** FastAPI, Uvicorn, Pydantic
* **Base de Données :** PostgreSQL, SQLAlchemy
* **Gestion de Dépendances :** Poetry
* **Conteneurisation :** Docker, Docker Compose (pour la BDD locale)
* **Déploiement :** Hugging Face Spaces
* **CI/CD :** GitHub Actions

## 📂 Structure du Projet

Le projet est organisé de la manière suivante :

```text
mon_projet_attrition/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── .env.example
├── Dockerfile
├── README.md
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml
├── requirements.txt
├── data/
│   └── raw/
        ├── extrait_sirh.csv
        ├── extrait_eval.csv
│       └── extrait_sondage.csv
├── models/
│   └── attrition_model.joblib
├── notebooks/
│   └── (vos notebooks ici, ex: 01_exploration.ipynb)
├── scripts/
│   └── populate_employees_table.py
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── config.py
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── load_data.py
│   │   └── preprocess.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database_setup.py
│   │   ├── init_db.py
│   │   └── models.py
│   └── modeling/
│       ├── __init__.py
│       ├── predict.py
│       └── train_model.py
└── tests/
    ├── __init__.py
    ├── functional/
    │   ├── __init__.py
    │   └── test_api.py
    └── unit/
        ├── __init__.py
        └── test_preprocess.py
```

## 🚀 Installation et Configuration Locale

**Prérequis :**

* [Git](https://git-scm.com/)
* [Python 3.12+](https://www.python.org/)
* [Poetry](https://python-poetry.org/docs/#installation) (pour la gestion des dépendances Python)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (ou Docker Engine + Docker Compose séparément sur Linux) pour la base de données PostgreSQL.

**Étapes :**

1.  **Clonez le repository :**
    ```bash
    git clone [URL_DE_VOTRE_REPO_GITHUB]
    cd mon_projet_attrition
    ```

2.  **Installez les dépendances Python avec Poetry :**
    ```bash
    poetry install
    ```
    *(Cela créera un environnement virtuel et installera toutes les dépendances listées dans `pyproject.toml`)*.

3.  **Configurez les Variables d'Environnement pour la Base de Données :**
    * Copiez le fichier d'exemple `.env.example` en `.env` :
        ```bash
        cp .env.example .env
        ```
    * Modifiez le fichier `.env` avec vos propres identifiants pour la base de données locale. Ce fichier est ignoré par Git.
        ```env
        # .env - VOS SECRETS LOCAUX
        POSTGRES_USER=votre_user_pg
        POSTGRES_PASSWORD=votre_mot_de_passe_pg_solide
        POSTGRES_DB=attrition_db_dev
        DB_HOST_PORT=5432
        ```

4.  **Démarrez le Service PostgreSQL avec Docker Compose :**
    Assurez-vous que Docker Desktop est en cours d'exécution.
    ```bash
    docker-compose up -d
    ```
    * Pour arrêter le service : `docker-compose down`
    * Pour voir les logs de la base de données : `docker-compose logs db`

5.  **Initialisez la Base de Données (Création des Tables) :**
    Activez d'abord l'environnement Poetry si ce n'est pas déjà fait (`poetry shell`).
    ```bash
    poetry run python -m src.database.init_db
    ```

6.  **Peuplez la Table `employees` (Données Initiales) :**
    Ce script charge les données des CSV, les nettoie et les insère dans la table `employees`.
    ```bash
    poetry run python -m scripts.populate_employees_table
    ```

7.  **Activez l'Environnement Virtuel Poetry (si pas déjà fait) :**
    ```bash
    poetry shell
    ```
    *(Votre terminal est maintenant configuré pour utiliser l'interpréteur Python et les librairies de cet environnement).*

## 📈 Usage

*(Assurez-vous d'être dans l'environnement Poetry : `poetry shell`, et que votre base de données PostgreSQL Docker est démarrée).*

1.  **Entraîner le modèle :**
    Le modèle sera entraîné en utilisant les données de la table `employees` de votre base PostgreSQL.
    ```bash
    python -m src.modeling.train_model
    ```
    *(Le modèle entraîné est sauvegardé dans `models/`)*.

2.  **Lancer l'API FastAPI :**
    ```bash
    uvicorn src.api.main:app --reload
    ```
    *(Le serveur démarrera sur `http://127.0.0.1:8000`. `--reload` permet le redémarrage automatique lors de modifications).*

## 🔌 API Endpoints

Une fois l'API lancée :

* **Documentation Interactive (Swagger UI) :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    * Explorez et testez les endpoints ici.
* **Health Check :** `GET /`
* **Prédiction Unique :** `POST /predict`
* **Prédiction en Masse :** `POST /predict_bulk`

Les appels à `/predict` et `/predict_bulk` sont enregistrés dans la table `api_prediction_logs` de la base de données PostgreSQL.

## ✅ Tests

Pour lancer la suite de tests (unitaires et fonctionnels) :
```bash
poetry run pytest
```

## 🗣️ Exemples d'Utilisation de l'API

L'API peut être testée interactivement via l'interface Swagger UI disponible à l'endpoint `/docs` lorsque le serveur API est lancé.

Pour des exemples de code permettant d'interagir avec l'API par programmation en utilisant `curl` (ligne de commande) ou Python (avec la librairie `requests`), veuillez consulter le document suivant :

➡️ **[Exemples d'Utilisation de l'API](./docs/API_USAGE_EXAMPLES.md)**

Voici un test rapide pour vérifier que l'API est en ligne (nécessite que l'API tourne sur `http://127.0.0.1:8000` et que `curl` soit installé) :

```bash
curl -X GET "[http://127.0.0.1:8000/](http://127.0.0.1:8000/)"
```

## 🛠️ Maintenance et Protocole de Mise à Jour

Pour assurer la pertinence et la performance continue de ce modèle de prédiction d'attrition, le protocole de mise à jour suivant est envisagé :

1.  **Surveillance des Performances :**
    * Les prédictions de l'API étant enregistrées dans la table `api_prediction_logs`, il sera possible (avec un outillage futur) de comparer ces prédictions aux départs réels observés pour évaluer la performance du modèle en continu.
    * Une baisse significative des métriques clés (ex: F2-score, rappel pour la classe "départ") indiquera un besoin de ré-évaluation.

2.  **Ré-entraînement du Modèle :**
    * **Fréquence :** Un ré-entraînement est à envisager :
        * Périodiquement (ex: tous les 6 mois ou annuellement) avec les données les plus récentes de la table `employees`.
        * Lorsque de nouvelles features pertinentes sont identifiées et ajoutées.
        * Si une dérive significative des données d'entrée est détectée.
        * Si les performances du modèle en production baissent en dessous d'un seuil acceptable.
    * **Procédure :** Le script `src/modeling/train_model.py` est utilisé pour le ré-entraînement. Le nouveau modèle sauvegardé devra ensuite être redéployé.

3.  **Mise à Jour des Données d'Entraînement :**
    * Un processus régulier (à définir) pour mettre à jour la table `employees` avec les données RH les plus récentes est nécessaire pour que les ré-entraînements soient basés sur des informations à jour. Cela pourrait impliquer de relancer périodiquement une version adaptée de `scripts/populate_employees_table.py` ou un pipeline ETL plus robuste.

4.  **Revue des Features :**
    * Périodiquement, il est bon de revoir la pertinence des features utilisées et d'explorer si de nouvelles données disponibles pourraient améliorer le modèle.

5.  **Mise à Jour des Dépendances :**
    * Les dépendances du projet (Python, librairies) doivent être mises à jour régulièrement pour des raisons de sécurité et pour bénéficier des dernières améliorations.
    * Utiliser `poetry show --outdated` pour identifier les dépendances obsolètes.
    * Mettre à jour avec `poetry update <nom_librairie>` ou `poetry update`.
    * **Crucial :** Après une mise à jour des dépendances, relancer l'intégralité des tests et potentiellement un ré-entraînement/évaluation pour s'assurer de la non-régression.

6.  **Documentation :**
    * Toute modification significative du modèle, des features, de l'architecture, ou du processus de ré-entraînement doit être reflétée dans cette documentation.

Ce protocole initial servira de base et pourra être affiné avec le temps et l'expérience acquise sur le modèle en production (ou en simulation de production).