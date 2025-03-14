# MonChat - Application de Chat IA Multimodale

MonChat est une application web interactive que j’ai mise en place en tant qu’étudiant pour explorer le fonctionnement des RAG, des agents IA et de Docker. Elle permet d’interagir avec différents types de contenu (PDF, CSV) via une interface de chat exploitant l’Intelligence Artificielle.

## 🎯 Objectif

Cette application vise à fournir une interface unifiée pour interagir avec différents types de contenu en utilisant l'Intelligence Artificielle. Elle permet aux utilisateurs de :
- Analyser et interroger des documents PDF
- Explorer et analyser des données CSV
- Générer du contenu pour des articles de blog
- Extraire et analyser du contenu web
- Interagir directement avec un modèle de langage

## 🚀 Fonctionnalités

- **Chat Classique** : Interaction directe avec le modèle Llama3.2
- **Chat PDF** : Analyse et interrogation de documents PDF
- **Chat CSV** : Analyse et interrogation de fichiers CSV
- **Chat Blog** : Génération d'articles de blog
- **Scrapper Web** : Extraction et analyse de contenu web
- **Chat CSV & Agent SQL** : Analyse et interrogation de fichiers CSV à l'aide de d'agent SQL

## 🏗️ Architecture

L'application est construite avec :
- **Frontend** : Streamlit pour l'interface utilisateur
- **Backend** : 
  - Ollama pour les modèles de langage
  - LangChain pour l'intégration IA
  - ChromaDB pour le stockage vectoriel
  - SQLAlchemy pour la gestion des données CSV

## 📋 Prérequis

- Docker (version 20.10 ou supérieure)
- Docker Compose (version 2.0 ou supérieure)
- Git
- Au moins 8GB de RAM recommandés
- 20GB d'espace disque libre recommandé

## 🛠️ Installation

1. Cloner le repository :
```bash
git clone https://github.com/amarcay/MonChat.git
cd MonChat
```

2. Créer les dossiers nécessaires :
```bash
mkdir -p data/CSV data/PDF chroma_db
```

3. Démarrer l'application avec Docker Compose :
```bash
docker-compose up --build
```

4. Télécharger le modèle Llama3.2 :
```bash
docker-compose exec ollama ollama pull llama3.2
```

## 🌐 Accès à l'Application

Une fois l'application démarrée, vous pouvez y accéder via votre navigateur :
- Interface principale : http://localhost:8501

## 📁 Structure du Projet

```
MonChat/
├── pages/
│   ├── 1_Le_Chat_du_PDF.py
│   ├── 2_Le_Chat_du_CSV.py
│   ├── 3_Le_Chat_du_BLOG.py
│   ├── 4_Le_Scrapper_Fou.py
│   └── 5_Le_Chat_du_CSV_et_L_Agent_SQL.py
├── data/
│   ├── CSV/
│   └── PDF/
├── chroma_db/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── Le_Classique_Chat.py
```

## 🔧 Configuration

### Variables d'Environnement

L'application utilise les variables d'environnement suivantes :
- `OLLAMA_HOST` : URL du service Ollama (configuré automatiquement dans docker-compose)
- `LANGSMITH_TRACING` : Activation du traçage LangSmith
- `LANGSMITH_API_KEY` : Clé API pour LangSmith
- `LANGSMITH_ENDPOINT` : Point d'accès LangSmith
- `LANGSMITH_PROJECT` : Nom du projet LangSmith

### Volumes Docker

- `data/` : Stockage des fichiers CSV et PDF
- `chroma_db/` : Base de données vectorielle
- `ollama_data` : Modèles Ollama

## 📦 Dépendances Principales

- **streamlit==1.32.0** : Interface utilisateur
- **langchain==0.1.12** : Framework d'intégration IA
- **ollama==0.1.6** : Client Ollama
- **pandas==2.2.1** : Manipulation des données
- **chromadb==0.4.24** : Base de données vectorielle
- **sentence-transformers==2.5.1** : Modèles d'embeddings
- **crewai==0.16.0** : Orchestration des agents IA

## 🚀 Utilisation

### Chat Classique
1. Accédez à l'interface principale
2. Posez vos questions directement dans le chat

### Chat PDF
1. Téléchargez un fichier PDF
2. Posez des questions sur son contenu
3. Le système analysera automatiquement le contenu et répondra à vos questions

### Chat CSV
1. Téléchargez un fichier CSV
2. Interrogez vos données
3. Le système analysera automatiquement le contenu et répondra à vos questions

### Chat Blog
1. Entrez un sujet
2. L'application générera un article complet
3. Le contenu sera structuré avec introduction, développement et conclusion

### Scrapper Web
1. Entrez une URL
2. L'application analysera le contenu du site
3. Obtenez un résumé et des insights sur le contenu

### Chat CSV & L'Agent SQL
1. Téléchargez un fichier CSV
2. Spécifiez le nom de la table
3. Interrogez vos données
4. Utilisez des requêtes naturelles pour analyser vos données

## 🛠️ Maintenance

### Redémarrage des Services
```bash
docker-compose restart
```

### Arrêt de l'Application
```bash
docker-compose down
```

### Voir les Logs
```bash
docker-compose logs -f
```

### Nettoyage des Données
```bash
# Supprimer les volumes Docker
docker-compose down -v

# Nettoyer les dossiers de données
rm -rf data/* chroma_db/*
```

## 🔍 Dépannage

### Problèmes Courants

1. **Erreur de connexion à Ollama**
   - Vérifiez que le service Ollama est en cours d'exécution
   - Assurez-vous que le modèle llama3.2 est téléchargé

2. **Problèmes de mémoire**
   - Augmentez la mémoire allouée à Docker
   - Fermez les applications non essentielles

3. **Erreurs de chargement de fichiers**
   - Vérifiez les permissions des dossiers data/
   - Assurez-vous que les fichiers ne sont pas corrompus

## 📝 Notes

- Les modèles Ollama sont stockés dans un volume Docker persistant
- Les fichiers CSV et PDF sont stockés localement dans le dossier `data/`
- La base de données vectorielle est stockée dans `chroma_db/`
- Le système utilise des embeddings pour une recherche sémantique efficace
- Les réponses sont générées en temps réel avec streaming

## 🔒 Sécurité

- Les fichiers sont traités localement
- Aucune donnée n'est envoyée à des services externes (sauf LangSmith si activé)
- Les fichiers temporaires sont nettoyés automatiquement

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

### Guidelines de Contribution

- Suivez les conventions de code Python (PEP 8)
- Ajoutez des tests pour les nouvelles fonctionnalités
- Mettez à jour la documentation si nécessaire
- Assurez-vous que tous les tests passent avant de soumettre une PR

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- Alphonse Marçay - [@amarcay](https://github.com/amarcay)
