# Étape 1: Utiliser une image Python 3.12 officielle et légère
FROM python:3.12-slim

# Variables d'environnement pour Python dans Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Définit un HOME accessible en écriture pour corriger les erreurs git config
ENV HOME=/tmp

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour la liste des paquets et installer les dépendances système
RUN apt-get update && \
    apt-get install -y wget tar git && \
    rm -rf /var/lib/apt/lists/*

# Copier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- AJOUTÉ ICI : Création des répertoires et gestion des permissions ---
# Créer les répertoires nécessaires pour les données et les modèles
RUN mkdir -p /app/data/raw /app/data/processed /app/models
# Donner la propriété à l'utilisateur 1000 (courant sur HF Spaces)
# Si vous avez des doutes sur l'utilisateur, HF utilise souvent 1000:1000 ou un utilisateur 'user'
RUN chown -R 1000:1000 /app/data /app/models
# --- FIN AJOUT ---

# Copier le code source
COPY ./src /app/src
# Ne copiez le dossier models que s'il contient des modèles pré-entraînés que vous voulez inclure dans l'image
# Si les modèles sont générés par train_model.py, ils seront sauvegardés dans /app/models créé ci-dessus.
# S'ils sont dans votre repo et que vous voulez les inclure, décommentez la ligne suivante et assurez-vous des permissions
# COPY ./models /app/models
# RUN chown -R 1000:1000 /app/models # Assurer les droits si modèles copiés

# Exposer le port
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]