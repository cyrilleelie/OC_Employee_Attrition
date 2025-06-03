api.main
========

.. py:module:: api.main

.. autoapi-nested-parse::

   Module principal de l'API FastAPI pour la prédiction d'attrition des employés.

   Définit les endpoints de l'API, gère le cycle de vie de l'application (chargement du modèle), valide les données d'entrée, appelle la logique de prédiction, et enregistre les interactions dans une base de données PostgreSQL.



Attributes
----------

.. autoapisummary::

   api.main.logger
   api.main.app


Functions
---------

.. autoapisummary::

   api.main.lifespan
   api.main.read_root
   api.main.predict_single
   api.main.predict_bulk


Module Contents
---------------

.. py:data:: logger

.. py:function:: lifespan(app: fastapi.FastAPI)
   :async:


   Gestionnaire de cycle de vie (lifespan) pour l'application FastAPI.

   Est exécuté au démarrage et à l'arrêt de l'application.
   Utilisé ici pour charger la pipeline de prédiction au démarrage.


.. py:data:: app

.. py:function:: read_root()
   :async:


   Endpoint racine pour vérifier la disponibilité et la version de l'API.


.. py:function:: predict_single(employee_data: api.schemas.EmployeeInput, db: sqlalchemy.orm.Session = Depends(get_db))
   :async:


   Prédit le risque d'attrition pour un seul employé.

   Les données de l'employé sont fournies dans le corps de la requête au format JSON.
   La prédiction (probabilité et classe) est retournée.
   L'input et l'output de la prédiction sont enregistrés en base de données.


.. py:function:: predict_bulk(input_data: api.schemas.BulkPredictionInput, db: sqlalchemy.orm.Session = Depends(get_db))
   :async:


   Prédit le risque d'attrition pour une liste d'employés.

   Les données des employés sont fournies dans le corps de la requête au format JSON,
   sous une clé "employees" contenant une liste d'objets employé.
   Retourne une liste de prédictions.
   Les inputs et outputs de chaque prédiction sont enregistrés en base de données.


