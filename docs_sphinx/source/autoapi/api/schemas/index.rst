api.schemas
===========

.. py:module:: api.schemas

.. autoapi-nested-parse::

   Définition des schémas Pydantic pour la validation des données de l'API.

   Ce module contient les modèles de données utilisés par FastAPI pour :

   * Valider les données des requêtes entrantes.
   * Sérialiser les données des réponses sortantes.
   * Générer automatiquement la documentation OpenAPI (Swagger UI).



Classes
-------

.. autoapisummary::

   api.schemas.EmployeeInput
   api.schemas.PredictionOutput
   api.schemas.BulkPredictionInput
   api.schemas.BulkPredictionOutput


Module Contents
---------------

.. py:class:: EmployeeInput(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Schéma Pydantic représentant les données d'entrée pour un employé
   lors d'une requête de prédiction d'attrition.

   Les champs correspondent aux données brutes attendues par la pipeline de preprocessing
   avant toute transformation majeure (scaling, one-hot encoding, etc.).
   Les descriptions et exemples aident à la compréhension et à l'utilisation de l'API.


   .. py:attribute:: age
      :type:  int
      :value: None



   .. py:attribute:: genre
      :type:  str
      :value: None



   .. py:attribute:: revenu_mensuel
      :type:  float
      :value: None



   .. py:attribute:: statut_marital
      :type:  str
      :value: None



   .. py:attribute:: departement
      :type:  str
      :value: None



   .. py:attribute:: poste
      :type:  str
      :value: None



   .. py:attribute:: nombre_experiences_precedentes
      :type:  int
      :value: None



   .. py:attribute:: annees_dans_l_entreprise
      :type:  int
      :value: None



   .. py:attribute:: satisfaction_employee_environnement
      :type:  int
      :value: None



   .. py:attribute:: satisfaction_employee_nature_travail
      :type:  int
      :value: None



   .. py:attribute:: satisfaction_employee_equipe
      :type:  int
      :value: None



   .. py:attribute:: satisfaction_employee_equilibre_pro_perso
      :type:  int
      :value: None



   .. py:attribute:: note_evaluation_precedente
      :type:  int
      :value: None



   .. py:attribute:: note_evaluation_actuelle
      :type:  int
      :value: None



   .. py:attribute:: heure_supplementaires
      :type:  str
      :value: None



   .. py:attribute:: augementation_salaire_precedente
      :type:  str
      :value: None



   .. py:attribute:: nombre_participation_pee
      :type:  int
      :value: None



   .. py:attribute:: nb_formations_suivies
      :type:  int
      :value: None



   .. py:attribute:: distance_domicile_travail
      :type:  int
      :value: None



   .. py:attribute:: niveau_education
      :type:  int
      :value: None



   .. py:attribute:: domaine_etude
      :type:  str
      :value: None



   .. py:attribute:: frequence_deplacement
      :type:  str
      :value: None



   .. py:attribute:: annees_depuis_la_derniere_promotion
      :type:  int
      :value: None



   .. py:method:: validate_genre(value: str) -> str
      :classmethod:



   .. py:method:: validate_heure_supplementaires(value: str) -> str
      :classmethod:



   .. py:method:: validate_frequence_deplacement(value: str) -> str
      :classmethod:



   .. py:method:: validate_statut_marital(value: str) -> str
      :classmethod:



   .. py:method:: validate_departement(value: str) -> str
      :classmethod:



   .. py:method:: validate_poste(value: str) -> str
      :classmethod:



   .. py:method:: validate_domaine_etude(value: str) -> str
      :classmethod:



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: PredictionOutput(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Schéma Pydantic pour la réponse d'une requête de prédiction.
   Inclut l'identifiant de l'employé (tel que retourné par la logique de prédiction),
   la probabilité de départ, et la classe prédite.


   .. py:attribute:: id_employe
      :type:  Union[str, int]


   .. py:attribute:: probabilite_depart
      :type:  float
      :value: None



   .. py:attribute:: prediction_depart
      :type:  int
      :value: None



.. py:class:: BulkPredictionInput(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Schéma Pydantic pour les requêtes de prédiction en masse.
   Attend une liste d'objets EmployeeInput.


   .. py:attribute:: employees
      :type:  List[EmployeeInput]


.. py:class:: BulkPredictionOutput(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Schéma Pydantic pour la réponse des prédictions en masse.
   Retourne une liste d'objets PredictionOutput.


   .. py:attribute:: predictions
      :type:  List[PredictionOutput]


