# Étape 1: Utiliser une image Python 3.12 officielle et légère
FROM python:3.12-slim

# Variables d'environnement pour Python dans Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/tmp # <--- AJOUTÉ ICI : Définit un HOME accessible en écriture

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour la liste des paquets et installer wget, tar ET git
RUN apt-get update && \
    apt-get install -y wget tar git && \
    rm -rf /var/lib/apt/lists/*

# Copier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code source et les modèles
COPY ./src /app/src
COPY ./models /app/models

# Exposer le port
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]