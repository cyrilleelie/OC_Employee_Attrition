# Guide de Contribution au Projet d'Attrition RH

Nous vous remercions de l'intérêt que vous portez à ce projet et de votre souhait d'y contribuer ! Ce guide a pour but de vous aider à comprendre comment contribuer de manière efficace.

## 🚀 Comment Commencer ?

1.  **Forker & Cloner (si vous n'êtes pas un collaborateur direct) :**
    * Si vous êtes un contributeur externe, "forkez" d'abord le dépôt, puis clonez votre fork.
    * Si vous êtes un collaborateur direct, clonez simplement le dépôt :
      ```bash
      git clone [URL_DU_REPO_GITHUB]
      cd nom-du-dossier-projet
      ```

2.  **Installer Poetry :**
    Ce projet utilise [Poetry](https://python-poetry.org/) pour la gestion des dépendances et des environnements virtuels. Suivez les [instructions d'installation officielles](https://python-poetry.org/docs/#installation).

3.  **Installer les Dépendances du Projet :**
    Une fois Poetry installé, à la racine du projet :
    ```bash
    poetry install
    ```
    Cela créera un environnement virtuel et installera toutes les dépendances nécessaires (y compris celles de développement).

4.  **Activer l'Environnement Virtuel :**
    ```bash
    poetry shell
    ```

5.  **Configurer les Variables d'Environnement (Base de Données) :**
    * Copiez le fichier d'exemple `.env.example` en `.env` :
      ```bash
      cp .env.example .env
      ```
    * Modifiez le fichier `.env` avec vos identifiants pour la base de données PostgreSQL locale (voir `README.md` pour plus de détails). Ce fichier est ignoré par Git.

6.  **Démarrer la Base de Données Locale (si nécessaire) :**
    Si vous travaillez sur des aspects nécessitant la base de données :
    ```bash
    docker-compose up -d
    ```
    N'oubliez pas d'initialiser les tables (`poetry run python -m src.database.init_db`) et de peupler les données (`poetry run python -m scripts.populate_employees_table`) si c'est votre première configuration.

## 🛠️ Workflow de Développement

Nous suivons un workflow basé sur Git pour assurer la qualité et la cohérence du code.

### 1. Branches

* **`main`** : Contient la version la plus stable et déployée. Aucun push direct n'est autorisé. Les modifications arrivent via des Pull Requests depuis `develop` après validation.
* **`develop`** : Branche principale d'intégration. Toutes les nouvelles fonctionnalités et corrections sont fusionnées ici avant de passer sur `main`. Aucun push direct n'est autorisé ; passez par une Pull Request.
* **Branches de Fonctionnalités/Corrections :**
    * Toujours créer une nouvelle branche à partir de la dernière version de `develop`.
    * Utilisez une convention de nommage claire :
        * Pour les nouvelles fonctionnalités : `feature/nom-court-de-la-feature` (ex: `feature/api-logging`)
        * Pour les corrections de bugs : `fix/description-bug` (ex: `fix/prediction-endpoint-500-error`)
        * Pour la documentation : `docs/sujet-documentation` (ex: `docs/update-contributing-guide`)
        * Pour les tâches diverses : `chore/description-tache` (ex: `chore/upgrade-dependencies`)
    ```bash
    git checkout develop
    git pull origin develop
    git checkout -b feature/ma-nouvelle-feature
    ```

### 2. Commits

* Rédigez des messages de commit clairs, concis et en français (ou en anglais si c'est la convention du projet).
* Utilisez les préfixes de **Conventional Commits** pour indiquer la nature du commit :
    * `feat:` (nouvelle fonctionnalité)
    * `fix:` (correction de bug)
    * `docs:` (changements dans la documentation)
    * `style:` (formatage, points-virgules manquants, etc. ; pas de changement de code)
    * `refactor:` (refonte du code qui ne corrige pas de bug ni n'ajoute de fonctionnalité)
    * `test:` (ajout ou correction de tests)
    * `chore:` (mise à jour de tâches de build, configuration, etc.)
    * `ci:` (changements dans les fichiers et scripts de CI/CD)
* Essayez de faire des commits atomiques (un changement logique par commit).

### 3. Qualité du Code

* **Formatage :** Nous utilisons **Black** pour le formatage automatique du code. Avant de commiter, lancez :
    ```bash
    poetry run black .
    ```
* **Linting :** Nous utilisons **Ruff** pour le linting (détection d'erreurs, de code smells, et application de règles de style). Avant de commiter, lancez :
    ```bash
    poetry run ruff check . --fix # Pour corriger automatiquement ce qui peut l'être
    poetry run ruff format . # Ruff peut aussi remplacer Black pour le formatage
    ```
    (Note: Le workflow CI vérifiera le formatage avec `black --check .` et le linting avec `ruff check .`)

### 4. Tests

* Toute nouvelle fonctionnalité ou correction de bug doit être accompagnée de **tests pertinents** (unitaires, fonctionnels, d'intégration).
* Assurez-vous que tous les tests passent localement avant de pousser votre code :
    ```bash
    poetry run pytest
    ```
* Vérifiez la couverture de test et essayez de la maintenir ou de l'augmenter :
    ```bash
    poetry run pytest --cov=src tests/
    ```
    (Note: Le workflow CI exécutera ces tests.)

## 🔄 Processus de Pull Request (PR)

1.  Une fois votre travail terminé sur votre branche de fonctionnalité, poussez votre branche sur GitHub :
    ```bash
    git push origin feature/ma-nouvelle-feature
    ```
2.  Sur GitHub, créez une **Pull Request** de votre branche de fonctionnalité vers la branche `develop`.
3.  Donnez un **titre clair** et une **description détaillée** à votre PR, expliquant les changements apportés et pourquoi.
4.  Assurez-vous que tous les **checks de la CI (GitHub Actions) passent** sur votre PR (formatage, linting, tests).
5.  Si vous travaillez en équipe, assignez un ou plusieurs relecteurs.
6.  Une fois la PR approuvée et les checks de la CI au vert, elle peut être fusionnée dans `develop` par un mainteneur du projet. Privilégiez le "Squash and merge" pour garder un historique propre sur `develop`.
7.  Après la fusion, la branche de fonctionnalité peut être supprimée sur GitHub et localement.

## 🐞 Rapporter des Bugs

* Utilisez l'onglet **"Issues"** du dépôt GitHub pour signaler les bugs.
* Veuillez inclure autant d'informations que possible :
    * Version du code (hash de commit ou tag).
    * Étapes pour reproduire le bug.
    * Comportement observé.
    * Comportement attendu.
    * Messages d'erreur complets et tracebacks.

## ✨ Proposer des Améliorations

* Les suggestions d'amélioration sont les bienvenues ! Veuillez ouvrir une **"Issue"** sur GitHub pour discuter de votre idée avant de commencer à développer.

## ❓ Questions ?

Si vous avez des questions sur la contribution, n'hésitez pas à ouvrir une "Issue" pour en discuter.

Merci pour votre contribution !