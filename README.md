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

Ce projet a pour objectif d'analyser les données RH afin de construire un modèle de Machine Learning capable de prédire le départ volontaire (attrition) des employés. Le modèle est ensuite exposé via une API RESTful construite avec FastAPI, prête à être déployée.

## 🎯 Objectifs

* **Analyser** les facteurs clés influençant l'attrition des employés.
* **Construire et Entraîner** un modèle de classification binaire performant.
* **Développer une API** pour obtenir des prédictions en temps réel pour un ou plusieurs employés.
* **Conteneuriser** l'application avec Docker pour un déploiement facile.
* **Déployer** l'API sur Hugging Face Spaces.
* *(Futur)* Intégrer les données avec une base de données PostgreSQL.

## 🛠️ Technologies Utilisées

* **Langage :** Python 3.12
* **Analyse & ML :** Pandas, NumPy, Scikit-learn, Joblib
* **API :** FastAPI, Uvicorn, Pydantic
* **Gestion de Dépendances :** Poetry
* **Conteneurisation :** Docker
* **Déploiement :** Hugging Face Spaces

## 📂 Structure du Projet

Le projet est organisé de la manière suivante :

* **`/data`**: Contient les données brutes et traitées (généralement non commitées).
* **`/notebooks`**: Pour l'exploration, les tests et la mise au point des modèles.
* **`/src`**: Le cœur de l'application Python.
    * **`/src/data_processing`**: Scripts pour charger et prétraiter les données.
    * **`/src/modeling`**: Scripts pour entraîner et utiliser le modèle.
    * **`/src/api`**: Scripts définissant l'API FastAPI (endpoints, schémas).
* **`/models`**: Stocke les modèles entraînés (potentiellement via Git LFS).
* **`/tests`**: Contient les tests unitaires et d'intégration.
* **Fichiers Racine**: `pyproject.toml`, `Dockerfile`, `README.md`, etc., pour la configuration et la documentation.

## 🚀 Installation Locale

**Prérequis :**

* [Git](https://git-scm.com/)
* [Python 3.12+](https://www.python.org/)
* [Poetry](https://python-poetry.org/docs/#installation)

**Étapes :**

1.  **Clonez le repository :**
    ```bash
    git clone [URL_DE_VOTRE_REPO_GITHUB]
    cd mon_projet_attrition
    ```
2.  **Installez les dépendances avec Poetry :**
    ```bash
    poetry install
    ```
3.  **(Optionnel mais Recommandé) Créez un fichier `.env` :** À la racine du projet, pour stocker d'éventuels secrets ou configurations locales. N'oubliez pas de l'ajouter au `.gitignore`.
4.  **Activez l'environnement virtuel :**
    ```bash
    poetry shell
    ```

## 📈 Usage

*(Assurez-vous d'être dans l'environnement Poetry : `poetry shell`)*

1.  **Préparer les données :** Placez vos fichiers CSV bruts dans `data/raw/`.
2.  **Entraîner le modèle :**
    ```bash
    python -m src.modeling.train_model
    ```
3.  **Lancer l'API FastAPI :**
    ```bash
    uvicorn src.api.main:app --reload
    ```

## 🔌 API Endpoints

Une fois l'API lancée, vous pouvez interagir avec elle :

* **Documentation Interactive (Swagger UI) :** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check :** `GET /`
* **Prédiction Unique :** `POST /predict`
* **Prédiction en Masse :** `POST /predict_bulk`

## ☁️ Déploiement

Cette application est conçue pour être déployée sur [Hugging Face Spaces](https://huggingface.co/spaces) en utilisant le `Dockerfile` fourni.

## 💡 Améliorations Futures

* Intégration d'une base de données PostgreSQL.
* Mise en place d'un monitoring du modèle.
* Création d'une interface utilisateur simple.
* Ajout de tests unitaires et d'intégration.

---