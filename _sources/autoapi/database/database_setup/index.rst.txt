database.database_setup
=======================

.. py:module:: database.database_setup

.. autoapi-nested-parse::

   Configuration centrale de SQLAlchemy pour la connexion à la base de données.

   Ce module initialise l'objet `engine` de SQLAlchemy, la fabrique de sessions `SessionLocal`, et la classe de base déclarative `Base` pour les modèles ORM. Il fournit également une fonction de dépendance (`get_db`) pour FastAPI afin de gérer les sessions de base de données par requête.



Attributes
----------

.. autoapisummary::

   database.database_setup.SQLALCHEMY_DATABASE_URL
   database.database_setup.engine
   database.database_setup.SessionLocal
   database.database_setup.Base


Functions
---------

.. autoapisummary::

   database.database_setup.create_db_tables
   database.database_setup.get_db


Module Contents
---------------

.. py:data:: SQLALCHEMY_DATABASE_URL

.. py:data:: engine
   :value: None


.. py:data:: SessionLocal

.. py:data:: Base

.. py:function:: create_db_tables()

   Crée toutes les tables dans la base de données définies par les modèles
   qui héritent de `Base`.

   Cette fonction est idempotente : elle ne créera les tables que si elles
   n'existent pas déjà.


.. py:function:: get_db() -> Generator[sqlalchemy.orm.Session, None, None]

   Dépendance FastAPI pour obtenir une session de base de données SQLAlchemy.

   Ce générateur crée une nouvelle session de base de données pour chaque requête entrante,
   la fournit à la fonction de chemin (endpoint), puis s'assure qu'elle est fermée
   après que la requête a été traitée (même en cas d'erreur).

   :Yields: *SQLAlchemySession* -- Une session de base de données SQLAlchemy.


