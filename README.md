# OC_Employee_Attrition - Projet de Prédiction de l'Attrition des Employés

Ce projet vise à développer un modèle de Machine Learning pour prédire la probabilité qu'un employé quitte l'entreprise, et à déployer ce modèle via une API et une interface web.

## Objectifs

* Analyser les facteurs clés de l'attrition.
* Construire un modèle prédictif performant.
* Mettre en place une API pour interroger le modèle (FastAPI).
* Intégrer les données dans une base PostgreSQL.
* Déployer une application de démonstration (Hugging Face Spaces).

## Structure du Projet



## Installation

1.  Clonez ce repository :
    ```bash
    git clone [URL_DE_VOTRE_REPO]
    cd mon_projet_attrition
    ```
2.  Assurez-vous d'avoir [Poetry](https://python-poetry.org/docs/#installation) installé.
3.  Installez les dépendances :
    ```bash
    poetry install
    ```
4.  Créez un fichier `.env` à la racine pour les configurations locales (voir `src/config.py`).
5.  Activez l'environnement virtuel :
    ```bash
    poetry shell
    ```

## Usage

### Entraînement du Modèle

```bash
poetry run python src/modeling/train_model.py
```