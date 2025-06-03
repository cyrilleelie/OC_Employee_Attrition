data_processing.load_data
=========================

.. py:module:: data_processing.load_data

.. autoapi-nested-parse::

   Module pour le chargement et la préparation initiale des données.

   Fonctions pour charger les données brutes depuis des fichiers CSV, les fusionner, et préparer les clés de jointure. Fournit également des fonctions pour charger les données depuis une base de données PostgreSQL une fois peuplée.
   La fonction principale `get_data` sert d'interface pour obtenir les données pour le reste de l'application, typiquement pour l'entraînement du modèle.



Attributes
----------

.. autoapisummary::

   data_processing.load_data.logger
   data_processing.load_data.data_from_db


Functions
---------

.. autoapisummary::

   data_processing.load_data.load_data_from_csv
   data_processing.load_data.load_data_from_postgres
   data_processing.load_data.get_data
   data_processing.load_data.load_and_merge_csvs


Module Contents
---------------

.. py:data:: logger

.. py:function:: load_data_from_csv(path: str = config.PROCESSED_DATA_PATH) -> pandas.DataFrame | None

   Charge les données depuis un unique fichier CSV spécifié.

   Utilisé comme fonction de secours ou pour charger un dataset déjà traité et sauvegardé en CSV.

   :param path: Chemin vers le fichier CSV.
                Par défaut, utilise config.PROCESSED_DATA_PATH.
   :type path: str, optional

   :returns:

             DataFrame Pandas contenant les données chargées,
                                  ou None si le fichier n'est pas trouvé.
   :rtype: pd.DataFrame | None


.. py:function:: load_data_from_postgres() -> pandas.DataFrame

   Charge l'intégralité des données de la table 'employees' depuis PostgreSQL
   dans un DataFrame Pandas.

   Utilise SQLAlchemy pour interagir avec la base de données configurée.

   :returns:

             DataFrame Pandas contenant les données de la table 'employees'.
                           Retourne un DataFrame vide en cas d'erreur ou si la table est vide.
   :rtype: pd.DataFrame


.. py:function:: get_data(source: str = 'postgres') -> pandas.DataFrame | None

   Fonction principale pour obtenir le jeu de données pour l'application.

   Sert d'interface pour charger les données soit depuis PostgreSQL (par défaut),
   soit depuis des fichiers CSV bruts (via `load_and_merge_csvs`).

   :param source: La source des données. Peut être "postgres" ou "csv".
                  Par défaut à "postgres".
   :type source: str, optional

   :returns:

             DataFrame Pandas contenant les données, ou None si une
                                  erreur majeure de chargement se produit (ex: CSV introuvables).
                                  Peut retourner un DataFrame vide si la source est vide (ex: table PG vide).
   :rtype: pd.DataFrame | None


.. py:function:: load_and_merge_csvs() -> pandas.DataFrame | None

   Charge les données depuis les trois fichiers CSV bruts (`extrait_sirh.csv`,
   `extrait_eval.csv`, `extrait_sondage.csv`), prépare les clés de jointure `id_employee`
   (notamment à partir de `eval_number` et `code_sondage`), et fusionne les DataFrames.

   Cette fonction est principalement utilisée pour le peuplement initial de la base de données.
   Elle s'assure que les `id_employee` sont traités comme des chaînes de caractères pour
   des fusions cohérentes.

   :returns:

             Un DataFrame fusionné contenant les données des trois sources,
                                  ou None si une erreur critique se produit (ex: fichier introuvable,
                                  colonne clé de jointure manquante).
   :rtype: pd.DataFrame | None


.. py:data:: data_from_db
   :value: None


