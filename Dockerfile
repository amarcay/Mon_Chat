# Utiliser une image Python officielle comme base
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p /app/data /app/chroma_db

# Exposer le port pour Streamlit
EXPOSE 8501

# Commande pour démarrer l'application
CMD ["streamlit", "run", "Le_Classique_Chat.py"] 