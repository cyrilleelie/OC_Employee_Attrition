# Étape 1: Utiliser une image Python officielle et légère comme base
FROM python:3.12-slim

# Définir une variable d'environnement pour éviter que Python ne mette en cache les .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Définir une variable d'environnement pour que Python fonctionne en mode non bufferisé (mieux pour les logs Docker)
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Mettre à jour la liste des paquets et installer wget, tar ET git
RUN apt-get update && \
    apt-get install -y wget tar git && \
    rm -rf /var/lib/apt/lists/*

# Copier UNIQUEMENT le fichier requirements.txt pour profiter du cache Docker
# Si requirements.txt ne change pas, Docker n'exécutera pas l'étape RUN suivante lors des builds ultérieurs
COPY requirements.txt .

# Mettre à jour pip et installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier TOUT le code source de l'application dans le conteneur
# Assurez-vous que .gitignore exclut bien les venv, .idea, __pycache__, etc.
COPY ./src /app/src
COPY ./models /app/models

# Exposer le port que FastAPI/Uvicorn utilisera (doit correspondre à la commande CMD)
EXPOSE 8000

# La commande à exécuter lorsque le conteneur démarre
# On utilise 0.0.0.0 pour que le serveur soit accessible depuis l'extérieur du conteneur
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]