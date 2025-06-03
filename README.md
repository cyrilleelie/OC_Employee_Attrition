---
title: API Prédiction Attrition RH
emoji: 📊
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 8000
license: mit
---

# Projet : Prédiction de l'Attrition des Employés et API

Ce projet a pour objectif d'analyser les données RH afin de construire un modèle de Machine Learning capable de prédire le départ volontaire (attrition) des employés. Le modèle est ensuite exposé via une API RESTful construite avec FastAPI, conteneurisée avec Docker, et déployée sur Hugging Face Spaces. Une documentation complète du projet et de l'API est également générée et déployée.

## 📚 Documentation Détaillée

Pour une documentation complète du projet, incluant le guide d'installation, les détails techniques du modèle, des exemples d'utilisation de l'API, le guide de contribution, et la référence de l'API générée à partir du code source, veuillez consulter :

➡️ **[Site de Documentation Déployé sur GitHub Pages](https://cyrilleelie.github.io/OC_Employee_Attrition/)**

*(Remplacez le lien ci-dessus par l'URL réelle de votre site GitHub Pages une fois qu'il sera actif).*

## 🎯 Objectifs

* Analyser les facteurs clés influençant l'attrition des employés.
* Construire et Entraîner un modèle de classification binaire performant.
* Développer une API pour obtenir des prédictions en temps réel.
* Intégrer une base de données PostgreSQL pour la gestion des données d'entraînement locales et l'enregistrement des prédictions de l'API locale.
* Conteneuriser l'application API avec Docker.
* Mettre en place un pipeline CI/CD robuste (tests, linting, build, déploiement de la documentation, création de releases).
* Déployer l'API sur Hugging Face Spaces.
* Produire une documentation technique et utilisateur complète.

## 🛠️ Technologies Utilisées

* **Langage :** Python 3.12
* **Analyse & ML :** Pandas, NumPy, Scikit-learn, Joblib
* **API :** FastAPI, Uvicorn, Pydantic
* **Base de Données (Locale) :** PostgreSQL, SQLAlchemy
* **Gestion de Dépendances :** Poetry
* **Conteneurisation :** Docker, Docker Compose
* **Documentation :** Sphinx, MyST-Parser, Sphinx-RTD-Theme, AutoAPI, GitHub Pages
* **CI/CD & Versioning :** Git, GitHub, GitHub Actions
* **Déploiement API :** Hugging Face Spaces

## 📂 Structure du Projet

Le projet est organisé de la manière suivante :

```text
mon_projet_attrition/
│
├── .github/
│   └── workflows/
│       ├── ci.yml            # Workflow CI (tests, lint, build docker)
│       └── deploy-docs.yml   # Workflow CD (déploiement documentation)
│       └── release.yml       # Workflow CD (création release GitHub)
├── .gitignore
├── .env.example            # Exemple pour variables d'environnement locales (BDD)
├── Dockerfile              # Pour l'image Docker de l'API
├── README.md               # Ce fichier
├── docker-compose.yml      # Pour lancer PostgreSQL localement
├── poetry.lock
├── pyproject.toml          # Dépendances et configuration Poetry
├── requirements.txt        # Export pour Docker/HF
│
├── data/
│   └── raw/                # Données CSV brutes initiales
│
├── docs_sphinx/            # Fichiers source de la documentation Sphinx
│   ├── source/
│   │   ├── conf.py         # Configuration Sphinx
│   │   ├── index.rst       # Page d'accueil de la documentation Sphinx
│   │   ├── installation_guide.rst
│   │   ├── model_documentation.md
│   │   ├── api_usage_examples.md
│   │   └── contributing.md
│   └── Makefile            # Pour construire la doc Sphinx localement
│
├── models/                 # Modèles ML entraînés (.joblib)
│
├── notebooks/              # Notebooks d'exploration initiaux
│
├── scripts/
│   └── populate_employees_table.py # Script de peuplement BDD
│
├── src/                    # Code source de l'application
│   ├── api/                # Code de l'API FastAPI
│   ├── config.py           # Configurations globales
│   ├── data_processing/    # Modules de chargement et preprocessing
│   ├── database/           # Modules BDD (setup, models, init_db)
│   └── modeling/           # Modules d'entraînement et prédiction
│
└── tests/
    ├── unit/               # Tests unitaires
    └── functional/         # Tests fonctionnels/API
```

## 🚀 Installation et Configuration Locale

Les instructions détaillées pour l'installation locale, la configuration de la base de données PostgreSQL avec Docker, et l'initialisation des données se trouvent dans notre documentation :

➡️ **[Consulter le Guide d'Installation Détaillé](https://cyrilleelie.github.io/OC_Employee_Attrition/installation_guide.html)**

*(Assurez-vous que ce lien pointe vers la bonne page une fois la documentation déployée).*

En résumé rapide :
1.  Clonez le dépôt.
2.  Installez Poetry.
3.  Exécutez `poetry install`.
4.  Configurez votre fichier `.env` à partir de `.env.example`.
5.  Lancez PostgreSQL : `docker-compose up -d`.
6.  Initialisez la BDD : `poetry run python -m src.database.init_db`.
7.  Peuplez la BDD : `poetry run python -m scripts.populate_employees_table`.
8.  Activez l'environnement : `poetry shell`.

## 📈 Usage Local

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
    *(API accessible sur `http://127.0.0.1:8000`. Les appels sont loggués en BDD locale si `ENABLE_API_DB_LOGGING=true` dans `.env`)*.

3.  **Construire et Consulter la Documentation Sphinx Localement :**
    ```bash
    cd docs_sphinx
    poetry run make html
    # Puis ouvrez docs_sphinx/build/html/index.html dans votre navigateur.
    ```

## 🔌 API Endpoints

* **Documentation Interactive (Swagger UI) :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Référence API (ReDoc) :** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check :** `GET /`
* **Prédiction Unique :** `POST /predict`
* **Prédiction en Masse :** `POST /predict_bulk`

Des exemples d'appels sont disponibles dans la [documentation détaillée](https://cyrilleelie.github.io/OC_Employee_Attrition/api_usage_examples.html).

## ✅ Tests

Pour lancer la suite de tests et voir la couverture :
```bash
poetry run pytest --cov=src tests/
