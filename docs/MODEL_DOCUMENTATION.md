# Documentation Technique du Modèle de Prédiction d'Attrition RH

## 1. Objectif du Modèle

Ce modèle de Machine Learning a pour objectif de prédire la probabilité qu'un employé quitte volontairement l'entreprise (attrition). Il vise à identifier les employés à risque afin de permettre des actions proactives de rétention.

## 2. Source et Préparation des Données

### 2.1. Source des Données
Les données utilisées pour l'entraînement et l'évaluation du modèle proviennent de la table `employees` de la base de données PostgreSQL du projet.
Initialement, ces données ont été consolidées à partir de trois fichiers CSV : `extrait_sirh.csv`, `extrait_eval.csv`, et `extrait_sondage.csv`.

### 2.2. Préparation des Données Avant Entraînement
Avant d'être stockées dans la base de données et utilisées par la pipeline d'entraînement Scikit-learn, les données brutes subissent les transformations suivantes (principalement via les scripts `src/data_processing/load_data.py` et `src/data_processing/preprocess.py` lors du peuplement de la base) :

* Fusion des différentes sources de données.
* Création de la clé `id_employee` (si nécessaire, à partir de `eval_number`).
* Nettoyage des données :
    * Conversion de la variable cible `a_quitte_l_entreprise` en format numérique (`0` pour Non, `1` pour Oui).
    * Conversion de la colonne `augmentation_salaire_precedente` (ex: "XX %") en valeur numérique (float).
    * Suppression des colonnes identifiées comme non pertinentes ou redondantes avant le feature engineering (ex: `eval_number` après utilisation).
    * Gestion des doublons.
* Mappage des variables binaires textuelles en format numérique (ex: `genre`, `heure_supplementaires`).
* (Optionnel) Création de features dérivées (ex: `satisfaction_moyenne` si vous l'avez implémentée et stockée).

## 3. Features Utilisées par le Modèle

Le modèle final est entraîné sur les features suivantes (après les étapes de préparation ci-dessus et avant le préprocessing Scikit-learn comme le scaling ou le one-hot encoding) :

* **Variables Numériques (destinées au Scaling) :**
    * `age`
    * `revenu_mensuel`
    * `nombre_experiences_precedentes`
    * `annees_dans_l_entreprise`
    * `satisfaction_employee_environnement`
    * `note_evaluation_precedente`
    * `satisfaction_employee_nature_travail`
    * `satisfaction_employee_equipe`
    * `satisfaction_employee_equilibre_pro_perso`
    * `note_evaluation_actuelle`
    * `augementation_salaire_precedente` (numérique)
    * `nombre_participation_pee`
    * `nb_formations_suivies`
    * `distance_domicile_travail`
    * `annees_depuis_la_derniere_promotion`
* **Variables Catégorielles Binaires (mappées en 0/1 avant préprocesseur) :**
    * `genre`
    * `heure_supplementaires`
* **Variables Catégorielles Ordinales (destinées à `OrdinalEncoder`) :**
    * `frequence_deplacement`
* **Variables Catégorielles Nominales (destinées à `OneHotEncoder` avec `drop='first'`) :**
    * `statut_marital`
    * `departement`
    * `poste`
    * `niveau_education`
    * `domaine_etude`

*(Note : La variable `id_employee` et les dates de métadonnées comme `date_creation_enregistrement` ne sont PAS utilisées comme features pour l'entraînement.)*

## 4. Algorithme et Configuration du Modèle

* **Algorithme Utilisé :** Régression Logistique (via `sklearn.linear_model.LogisticRegression`).
* **Motivation (brève) :** Choisi pour sa simplicité, son interprétabilité et ses bonnes performances sur les problèmes de classification binaire, surtout après un bon preprocessing des features. C'est un bon point de départ.
* **Hyperparamètres Clés :**
    * `random_state=42` (pour la reproductibilité).
    * `class_weight='balanced'` (pour aider à gérer le déséquilibre des classes dans la variable cible).
    * `max_iter=1000` (pour assurer la convergence).
    * *(Autres hyperparamètres importants si vous les avez modifiés)*.

## 5. Métriques de Performance (sur le Jeu de Test)

Les performances du modèle sont évaluées sur un jeu de test mis de côté (20% des données). Voici les résultats obtenus lors du dernier entraînement :

*(ICI, copiez-collez la sortie de la Matrice de Confusion et du Rapport de Classification de votre script `train_model.py`)*

* **Matrice de Confusion :**
    ```
    # Exemple
    [[194  53]
    [ 13  34]]
    ```
* **Rapport de Classification :**
    ```
    # Exemple
                  precision    recall  f1-score   support

             Non       0.94      0.79      0.85       247
             Oui       0.39      0.72      0.51        47

        accuracy                           0.78       294
       macro avg       0.66      0.75      0.68       294
    weighted avg       0.85      0.78      0.80       294
    ```

## 7. Procédure de Ré-entraînement

Pour ré-entraîner le modèle (par exemple, si de nouvelles données sont disponibles dans la table `employees`) :

1.  Assurez-vous que l'environnement Poetry est actif (`poetry shell`).
2.  Exécutez le script d'entraînement :
    ```bash
    python -m src.modeling.train_model
    ```
3.  Le nouveau modèle (`.joblib`) sera sauvegardé dans le dossier `models/`, écrasant l'ancien.
4.  Si l'API est déployée, il faudra redéployer l'application avec le nouveau fichier modèle.

## 8. Considérations de Maintenance et Monitoring

* **Monitoring des Données d'Entrée :** Surveiller la distribution des données reçues par l'API pour détecter une éventuelle dérive par rapport aux données d'entraînement.
* **Monitoring des Performances :** Si possible, suivre la performance réelle du modèle sur les nouvelles prédictions (nécessiterait un feedback sur les départs réels).
* **Ré-entraînement Périodique :** Envisager un ré-entraînement régulier (ex: trimestriel, semestriel) avec des données fraîches pour maintenir la pertinence du modèle.

## 9. Architecture du Projet

Le projet est structuré autour de plusieurs composants clés qui interagissent pour fournir la fonctionnalité de prédiction d'attrition :

1.  **Sources de Données Brutes :**
    * Initialement, les données proviennent de trois fichiers CSV (`extrait_sirh.csv`, `extrait_eval.csv`, `extrait_sondage.csv`).
2.  **Base de Données (PostgreSQL) :**
    * Un service PostgreSQL (géré localement via Docker Compose) stocke :
        * La table `employees` : Contient les données fusionnées, nettoyées et prétraitées (mappages binaires, conversion "XX %") prêtes pour l'entraînement du modèle et la consultation. Elle est peuplée via le script `scripts/populate_employees_table.py`.
        * La table `api_prediction_logs` : Enregistre les requêtes envoyées à l'API et les prédictions retournées.
3.  **Préparation des Données pour l'Entraînement (`src/data_processing/`) :**
    * `load_data.py` : Charge les données depuis la table `employees` de PostgreSQL vers un DataFrame Pandas.
    * `preprocess.py` : Contient les fonctions pour les transformations finales avant l'application du préprocesseur Scikit-learn (ex: `create_features`). Les fonctions `clean_data` et `map_binary_features` sont principalement utilisées pour la préparation des données *avant* leur insertion en base.
4.  **Entraînement du Modèle (`src/modeling/train_model.py`) :**
    * Ce script orchestre le chargement des données depuis la BDD.
    * Il sépare les données en ensembles d'entraînement et de test.
    * Il construit et ajuste (`fit`) une `Pipeline` Scikit-learn qui inclut :
        * Un `ColumnTransformer` (défini dans `preprocess.py`) pour le scaling des numériques, l'encodage One-Hot des catégorielles nominales, et l'encodage ordinal des catégorielles ordinales.
        * Le classifieur (ex: `LogisticRegression`).
    * Il évalue le modèle et sauvegarde la pipeline entraînée dans `models/attrition_model.joblib`.
5.  **API de Prédiction (`src/api/`) :**
    * Construite avec FastAPI (`main.py`).
    * Définit les schémas d'entrée/sortie avec Pydantic (`schemas.py`).
    * L'endpoint `/predict` (et `/predict_bulk`) :
        * Reçoit les données brutes de l'employé.
        * Appelle la fonction `predict_attrition` de `src/modeling/predict.py`.
        * `predict_attrition` applique les transformations initiales nécessaires (celles de `clean_data`, `map_binary_features`, `create_features` sur les données brutes) puis utilise la `Pipeline` Scikit-learn chargée pour faire la prédiction.
        * Enregistre l'input et l'output dans la table `api_prediction_logs` via SQLAlchemy.
6.  **Conteneurisation (Docker) :**
    * `Dockerfile` : Décrit comment construire l'image de l'API FastAPI pour le déploiement.
    * `docker-compose.yml` : Utilisé pour lancer et gérer le service PostgreSQL localement.
7.  **Gestion des Dépendances (Poetry) :**
    * `pyproject.toml` et `poetry.lock` gèrent les dépendances Python et l'environnement virtuel.
8.  **Intégration Continue (GitHub Actions) :**
    * Le fichier `.github/workflows/ci.yml` automatise les linters et les tests à chaque push/pull request.
9.  **Déploiement (Hugging Face Spaces) :**
    * L'API conteneurisée est déployée sur Hugging Face Spaces.

*(Optionnel : Vous pourriez insérer ici un schéma simplifié si vous en avez un, même textuel, ou un lien vers une image hébergée)*

## 10. Justification des Choix Techniques (Ajoutez à MODEL_DOCUMENTATION.md ou nouveau fichier)

Les principaux choix technologiques pour ce projet ont été faits pour répondre aux besoins de développement, de déploiement et de maintenabilité :

* **Python :** Langage de prédilection pour la Data Science et le Machine Learning grâce à son écosystème riche (Pandas, Scikit-learn, etc.).
* **Pandas :** Pour la manipulation et l'analyse efficaces des données tabulaires.
* **Scikit-learn :** Pour la construction de la pipeline de preprocessing et l'entraînement du modèle de classification.
* **Poetry :** Pour une gestion moderne et robuste des dépendances Python, assurant la reproductibilité des environnements.
* **FastAPI :** Framework web Python choisi pour sa haute performance, sa facilité d'utilisation, la validation des données intégrée via Pydantic, et la génération automatique de documentation API (Swagger UI/OpenAPI). Ses capacités asynchrones sont également un atout pour des API réactives.
* **Pydantic :** Utilisé par FastAPI pour la validation des types de données des requêtes et des réponses, garantissant la robustesse des échanges avec l'API.
* **PostgreSQL :** Système de gestion de base de données relationnelle open-source, puissant, fiable et bien adapté pour stocker les données structurées du projet et les logs de prédiction. Le support du type `JSONB` est utile pour stocker les inputs bruts de l'API.
* **SQLAlchemy :** ORM Python utilisé pour interagir avec la base de données PostgreSQL de manière plus pythonique et pour faciliter la définition des modèles de table et les migrations de schéma (bien que nous n'ayons pas encore abordé les migrations).
* **Docker & Docker Compose :** Pour la conteneurisation. Docker permet d'empaqueter l'API FastAPI et ses dépendances pour un déploiement cohérent. Docker Compose simplifie la gestion du service PostgreSQL en développement local.
* **Hugging Face Spaces :** Plateforme choisie pour sa simplicité de déploiement et d'hébergement gratuit pour les applications et API liées au Machine Learning, avec une bonne intégration Git et Docker.
* **GitHub & GitHub Actions :** Pour la gestion de version du code source et la mise en place d'un pipeline d'intégration continue (CI) afin d'automatiser les tests et les vérifications de qualité du code.
* **Pytest :** Framework de test pour Python, utilisé pour écrire des tests unitaires et fonctionnels afin d'assurer la fiabilité du code.
* **Ruff / Black :** Outils de linting et de formatage pour maintenir une haute qualité et une cohérence du style de code.

Ces outils ont été choisis pour leur popularité, leur maturité, leur bonne documentation et leur adéquation avec les objectifs d'un projet MLOps moderne.