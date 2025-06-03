database.init_db
================

.. py:module:: database.init_db

.. autoapi-nested-parse::

   Script pour initialiser la base de données.

   Ce module contient la logique pour créer toutes les tables définies dans les modèles SQLAlchemy (via src.database.models) dans la base de données configurée (via src.database.database_setup.engine).

   Ce script est généralement exécuté une fois pour mettre en place le schéma de la base de données, ou après des modifications de schéma si les tables doivent être recréées (attention, la recréation peut entraîner une perte de données si les tables existent déjà et ne sont pas vidées au préalable).



Attributes
----------

.. autoapisummary::

   database.init_db.logger


Functions
---------

.. autoapisummary::

   database.init_db.create_tables


Module Contents
---------------

.. py:data:: logger

.. py:function:: create_tables()

   Crée toutes les tables définies dans les modèles SQLAlchemy.

   Utilise l'objet `engine` global et la métadonnée de `Base` pour émettre
   les commandes DDL (Data Definition Language) appropriées afin de créer
   les tables dans la base de données si elles n'existent pas déjà.

   Enregistre des messages d'information sur le succès ou l'échec de l'opération.

   :raises SQLAlchemyError: Si une erreur se produit lors de l'interaction avec la base de données
       pendant la création des tables.


