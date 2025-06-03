data_processing.preprocess
==========================

.. py:module:: data_processing.preprocess

.. autoapi-nested-parse::

   Module de prétraitement des données pour le projet d'attrition RH.

   Ce module contient les fonctions nécessaires pour :

   * Mapper les features binaires.
   * Nettoyer les données brutes (conversion de la cible, suppression de colonnes, gestion des doublons, conversion de types spécifiques comme les pourcentages).
   * Créer de nouvelles features (feature engineering) - actuellement un placeholder.
   * Construire une pipeline de prétraitement Scikit-learn (ColumnTransformer) pour l'imputation, la mise à l'échelle des numériques, et l'encodage des catégorielles (OneHot et Ordinal).
   * Exécuter l'ensemble de ce pipeline de preprocessing.



Attributes
----------

.. autoapisummary::

   data_processing.preprocess.logger
   data_processing.preprocess.df_raw


Functions
---------

.. autoapisummary::

   data_processing.preprocess.map_binary_features
   data_processing.preprocess.clean_data
   data_processing.preprocess.create_features
   data_processing.preprocess.build_preprocessor
   data_processing.preprocess.run_preprocessing_pipeline


Module Contents
---------------

.. py:data:: logger

.. py:function:: map_binary_features(df: pandas.DataFrame, binary_cols_map: dict) -> pandas.DataFrame

   Mappe les valeurs des colonnes catégorielles binaires spécifiées en 0 et 1.

   :param df: DataFrame d'entrée.
   :type df: pd.DataFrame
   :param binary_cols_map: Dictionnaire où les clés sont les noms de colonnes
                           et les valeurs sont des dictionnaires de mapping
                           (ex: {'Oui': 1, 'Non': 0}).
   :type binary_cols_map: dict

   :returns: DataFrame avec les colonnes binaires mappées.
   :rtype: pd.DataFrame


.. py:function:: clean_data(df: pandas.DataFrame) -> pandas.DataFrame

   Applique les étapes de nettoyage de base et les conversions de types spécifiques.

   - Convertit la variable cible textuelle en format numérique.
   - Supprime les colonnes jugées inutiles ou redondantes.
   - Supprime les lignes dupliquées.
   - Convertit la colonne 'augementation_salaire_precedente' (texte en "XX %") en numérique.

   :param df: DataFrame d'entrée brut ou fusionné.
   :type df: pd.DataFrame

   :returns: DataFrame nettoyé.
   :rtype: pd.DataFrame

   :raises ValueError: Si la colonne cible 'a_quitte_l_entreprise' est manquante.


.. py:function:: create_features(df: pandas.DataFrame) -> pandas.DataFrame

   Crée de nouvelles features (ingénierie des features) à partir des colonnes existantes.

   :param df: DataFrame d'entrée (généralement après nettoyage et mappage binaire).
   :type df: pd.DataFrame

   :returns: DataFrame avec les nouvelles features ajoutées.
   :rtype: pd.DataFrame


.. py:function:: build_preprocessor(numerical_cols: list, onehot_cols: list, ordinal_cols: list, ordinal_categories_map: dict) -> sklearn.compose.ColumnTransformer

   Construit et retourne un objet ColumnTransformer de Scikit-learn pour le prétraitement.

   Le ColumnTransformer applique :
   - Imputation par la médiane puis StandardScaler aux colonnes numériques.
   - Imputation par la valeur la plus fréquente puis OneHotEncoder aux colonnes catégorielles nominales.
   - Imputation par la valeur la plus fréquente puis OrdinalEncoder aux colonnes catégorielles ordinales.

   :param numerical_cols: Liste des noms des colonnes numériques.
   :type numerical_cols: list
   :param onehot_cols: Liste des noms des colonnes catégorielles à encoder en One-Hot.
   :type onehot_cols: list
   :param ordinal_cols: Liste des noms des colonnes catégorielles ordinales.
   :type ordinal_cols: list
   :param ordinal_categories_map: Dictionnaire spécifiant l'ordre des catégories
                                  pour chaque colonne ordinale.
                                  Format: {'nom_col_ord': ['cat1', 'cat2', ...]}
   :type ordinal_categories_map: dict

   :returns: Objet ColumnTransformer configuré mais non ajusté.
   :rtype: ColumnTransformer

   :raises ValueError: Si les catégories pour une colonne ordinale ne sont pas définies
       dans `ordinal_categories_map`.


.. py:function:: run_preprocessing_pipeline(df: pandas.DataFrame, binary_cols_map: dict = None, ordinal_cols_categories_map: dict = None, preprocessor: sklearn.compose.ColumnTransformer = None, fit: bool = False)

   Exécute le pipeline de preprocessing complet sur le DataFrame fourni.

   Orchestre les étapes de nettoyage, mappage binaire, création de features,
   et application (ajustement ou transformation) du ColumnTransformer.

   :param df: DataFrame d'entrée brut.
   :type df: pd.DataFrame
   :param binary_cols_map: Mapping pour les features binaires.
                           Utilise config.BINARY_FEATURES_MAPPING si non fourni (dans l'appelant).
   :type binary_cols_map: dict, optional
   :param ordinal_cols_categories_map: Catégories pour les features ordinales.
                                       Utilise config.ORDINAL_FEATURES_CATEGORIES si non fourni (dans l'appelant).
   :type ordinal_cols_categories_map: dict, optional
   :param preprocessor: Un ColumnTransformer pré-ajusté.
                        Requis si `fit` est False.
   :type preprocessor: ColumnTransformer, optional
   :param fit: Si True, le préprocesseur est ajusté (`fit_transform`) sur les données.
               Si False, le `preprocessor` fourni est utilisé pour transformer (`transform`) les données.
               Par défaut à False.
   :type fit: bool, optional

   :returns:

             Contenant selon le mode `fit`:
                    Si `fit` est True: (X_processed_df, y_series, fitted_processor_instance)
                    Si `fit` est False: (X_processed_df, y_series)
                    Où X_processed_df est un DataFrame et y_series est une Series.
   :rtype: Tuple

   :raises ValueError: Si la colonne cible est manquante après les premières étapes,
       ou si `fit` est False et aucun `preprocessor` n'est fourni,
       ou si une colonne ordinale spécifiée n'existe pas dans le DataFrame.


.. py:data:: df_raw

