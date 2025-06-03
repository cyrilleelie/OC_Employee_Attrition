modeling.predict
================

.. py:module:: modeling.predict

.. autoapi-nested-parse::

   Module pour charger la pipeline de Machine Learning entraînée et effectuer des prédictions.

   Fonctions principales :

   * `load_prediction_pipeline()`: Charge la pipeline Scikit-learn sauvegardée (modèle + préprocesseur).
   * `predict_attrition()`: Prend des données brutes d'employés en entrée (DataFrame), applique les transformations de preprocessing initiales, puis utilise la pipeline chargée pour prédire la probabilité d'attrition et la classe de départ.



Attributes
----------

.. autoapisummary::

   modeling.predict.logger
   modeling.predict.sample_data_dict


Functions
---------

.. autoapisummary::

   modeling.predict.load_prediction_pipeline
   modeling.predict.predict_attrition


Module Contents
---------------

.. py:data:: logger

.. py:function:: load_prediction_pipeline() -> Any | None

   Charge la pipeline de prédiction complète (préprocesseur + modèle) depuis le disque.

   La pipeline est chargée une seule fois et stockée dans une variable globale `_pipeline`
   pour optimiser les appels suivants.

   :returns:

             L'objet pipeline Scikit-learn chargé, ou None si une erreur
                              se produit (ex: fichier non trouvé, erreur de chargement).
   :rtype: Pipeline | None


.. py:function:: predict_attrition(input_data: pandas.DataFrame) -> Union[List[Dict[str, Any]], Dict[str, str]]

   Prédit le risque d'attrition pour les employés fournis en entrée.

   Cette fonction prend un DataFrame de données brutes, applique les étapes
   de preprocessing initiales (nettoyage, mappage binaire, création de features)
   puis utilise la pipeline Scikit-learn entraînée et chargée pour effectuer
   les prédictions.

   :param input_data: DataFrame contenant les données brutes des employés
                      pour lesquels faire une prédiction. Les colonnes doivent
                      correspondre aux attentes de `clean_data` et
                      `map_binary_features` (format brut).
   :type input_data: pd.DataFrame

   :returns:

                 - Une liste de dictionnaires si la prédiction réussit, chaque dictionnaire
                   contenant 'id_employe', 'probabilite_depart', 'prediction_depart'.
                 - Un dictionnaire d'erreur `{"error": "message"}` si la pipeline n'est pas
                   chargée ou si une autre erreur majeure se produit.
   :rtype: Union[List[Dict[str, Any]], Dict[str, str]]


.. py:data:: sample_data_dict

