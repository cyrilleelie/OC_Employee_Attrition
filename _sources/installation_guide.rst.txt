.. _installation_guide:

Guide d'Installation
====================

Ce guide détaille les étapes nécessaires pour configurer l'environnement de développement local et lancer le projet de prédiction d'attrition RH.

Prérequis
---------

Avant de commencer, assurez-vous d'avoir les outils suivants installés sur votre système :

* `Git <https://git-scm.com/>`_
* `Python 3.12+ <https://www.python.org/>`_
* `Poetry <https://python-poetry.org/docs/#installation>`_ (pour la gestion des dépendances Python)
* `Docker Desktop <https://www.docker.com/products/docker-desktop/>`_ (ou Docker Engine + Docker Compose sur Linux) pour la base de données PostgreSQL.

Étapes d'Installation
---------------------

1.  **Cloner le Dépôt :**
    Ouvrez un terminal et clonez le dépôt GitHub du projet :

    .. code-block:: bash

       git clone [URL_DE_VOTRE_REPO_GITHUB]
       cd nom-du-dossier-projet

    Remplacez `[URL_DE_VOTRE_REPO_GITHUB]` par l'URL actuelle de votre dépôt et `nom-du-dossier-projet` par le nom du dossier créé.

2.  **Installer les Dépendances Python :**
    À la racine du projet cloné, utilisez Poetry pour installer les dépendances :

    .. code-block:: bash

       poetry install

    Cette commande créera un environnement virtuel dédié et installera tous les packages listés dans `pyproject.toml`.

3.  **Configurer les Variables d'Environnement pour la Base de Données :**
    Le projet utilise un fichier `.env` pour gérer les identifiants de la base de données locale.

    * Copiez le fichier d'exemple `.env.example` (situé à la racine du projet) en un nouveau fichier nommé `.env` :

      .. code-block:: bash

         cp .env.example .env

    * Ouvrez le fichier `.env` et remplacez les placeholders par vos identifiants PostgreSQL locaux. Par exemple :

      .. code-block:: text

         # .env - Vos secrets locaux
         POSTGRES_USER=mon_user_local
         POSTGRES_PASSWORD=mon_mot_de_passe_secret
         POSTGRES_DB=attrition_dev_db
         DB_HOST_PORT=5432

    **Note :** Le fichier `.env` est listé dans `.gitignore` et ne doit pas être commité.

4.  **Démarrer le Service PostgreSQL :**
    Assurez-vous que Docker Desktop est en cours d'exécution. Puis, depuis la racine du projet, lancez le service PostgreSQL défini dans `docker-compose.yml` :

    .. code-block:: bash

       docker-compose up -d

    Pour vérifier que le conteneur est bien lancé : `docker ps`.
    Pour arrêter le service : `docker-compose down`.

5.  **Initialiser la Base de Données (Créer les Tables) :**
    Une fois le service PostgreSQL démarré, activez l'environnement Poetry (si ce n'est pas déjà fait) et lancez le script d'initialisation :

    .. code-block:: bash

       poetry shell  # Si vous n'êtes pas déjà dans le shell Poetry
       python -m src.database.init_db

6.  **Peupler la Table `employees` (Données Initiales) :**
    Ce script charge les données des CSV sources, les nettoie et les insère dans la table `employees`.

    .. code-block:: bash

       python -m scripts.populate_employees_table

Activation de l'Environnement
-----------------------------

Pour travailler sur le projet, activez l'environnement virtuel créé par Poetry :

.. code-block:: bash

   poetry shell

Votre terminal est maintenant configuré pour utiliser l'interpréteur Python et les librairies de cet environnement.

Lancer l'API Localement
------------------------

Une fois l'environnement configuré et la base de données initialisée et peuplée :

.. code-block:: bash

   uvicorn src.api.main:app --reload

L'API sera accessible sur `http://127.0.0.1:8000` et la documentation interactive sur `http://127.0.0.1:8000/docs`.

Lancer les Tests
----------------

Pour exécuter la suite de tests :

.. code-block:: bash

   poetry run pytest