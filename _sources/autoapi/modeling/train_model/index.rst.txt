modeling.train_model
====================

.. py:module:: modeling.train_model

.. autoapi-nested-parse::

   Module d'entraînement et d'évaluation du modèle de prédiction d'attrition.

   Ce script orchestre le pipeline complet de Machine Learning :

   1. Chargement des données prétraitées depuis la source configurée (PostgreSQL).
   2. (Optionnel) Création de features supplémentaires.
   3. Séparation des données en ensembles d'entraînement et de test.
   4. Identification des types de colonnes pour le preprocessing.
   5. Construction d'une pipeline Scikit-learn incluant :
       * Un préprocesseur (ColumnTransformer) pour imputer, scaler (numériques) et encoder (catégorielles OneHot et Ordinal).
       * Un classifieur (actuellement LogisticRegression).
   6. Entraînement de la pipeline complète sur les données d'entraînement.
   7. Évaluation du modèle sur les données de test (Matrice de confusion, rapport de classification, F2-score).
   8. Sauvegarde de la pipeline entraînée pour une utilisation ultérieure (prédictions).



Attributes
----------

.. autoapisummary::

   modeling.train_model.logger


Functions
---------

.. autoapisummary::

   modeling.train_model.train_and_evaluate_pipeline


Module Contents
---------------

.. py:data:: logger

.. py:function:: train_and_evaluate_pipeline()

   Orchestre le chargement des données, la préparation, l'entraînement d'un modèle
   de classification, son évaluation, et la sauvegarde de la pipeline entraînée.

   Cette fonction est le point d'entrée principal pour le processus d'entraînement.
   Elle utilise les configurations définies dans `config.py` et les fonctions
   de `load_data.py` et `preprocess.py`.

   Le modèle actuel est une Régression Logistique, et la métrique principale
   d'évaluation est le F2-score pour la classe positive (départ d'employé).

   :raises ValueError: Si la colonne cible n'est pas trouvée dans les données
       après les étapes initiales de chargement et de feature engineering.


