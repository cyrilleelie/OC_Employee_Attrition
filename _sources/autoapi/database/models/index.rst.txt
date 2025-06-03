database.models
===============

.. py:module:: database.models

.. autoapi-nested-parse::

   Définition des modèles SQLAlchemy ORM pour les tables de la base de données.

   Ce module contient les classes Python qui mappent aux tables de la base de données PostgreSQL, en utilisant la Base déclarative de SQLAlchemy.
   Chaque classe représente une table, et ses attributs de classe représentent les colonnes de cette table.



Classes
-------

.. autoapisummary::

   database.models.Employee
   database.models.ApiPredictionLog


Module Contents
---------------

.. py:class:: Employee

   Bases: :py:obj:`database.database_setup.Base`


   Modèle SQLAlchemy représentant un employé et ses caractéristiques.
   Mappe à la table 'employees' dans la base de données.
   Cette table contient les données fusionnées et prétraitées utilisées
   pour l'entraînement du modèle d'attrition et potentiellement pour
   enrichir les informations lors des prédictions.


   .. py:attribute:: id_employee


   .. py:attribute:: age


   .. py:attribute:: genre


   .. py:attribute:: revenu_mensuel


   .. py:attribute:: statut_marital


   .. py:attribute:: departement


   .. py:attribute:: poste


   .. py:attribute:: nombre_experiences_precedentes


   .. py:attribute:: annees_dans_l_entreprise


   .. py:attribute:: satisfaction_employee_environnement


   .. py:attribute:: note_evaluation_precedente


   .. py:attribute:: satisfaction_employee_nature_travail


   .. py:attribute:: satisfaction_employee_equipe


   .. py:attribute:: satisfaction_employee_equilibre_pro_perso


   .. py:attribute:: note_evaluation_actuelle


   .. py:attribute:: heure_supplementaires


   .. py:attribute:: augementation_salaire_precedente


   .. py:attribute:: nombre_participation_pee


   .. py:attribute:: nb_formations_suivies


   .. py:attribute:: distance_domicile_travail


   .. py:attribute:: niveau_education


   .. py:attribute:: domaine_etude


   .. py:attribute:: frequence_deplacement


   .. py:attribute:: annees_depuis_la_derniere_promotion


   .. py:attribute:: a_quitte_l_entreprise_numeric


   .. py:attribute:: date_creation_enregistrement


   .. py:attribute:: date_derniere_modification


.. py:class:: ApiPredictionLog

   Bases: :py:obj:`database.database_setup.Base`


   Modèle SQLAlchemy pour enregistrer les appels à l'API de prédiction.
   Mappe à la table 'api_prediction_logs'. Chaque enregistrement correspond
   à une requête de prédiction, incluant les données d'entrée et le résultat.


   .. py:attribute:: log_id


   .. py:attribute:: timestamp_requete


   .. py:attribute:: employee_id_concerne


   .. py:attribute:: input_data


   .. py:attribute:: prediction_probabilite


   .. py:attribute:: prediction_classe


   .. py:attribute:: version_modele


