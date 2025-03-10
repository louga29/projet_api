# Projet d'Analyse de Données et API Web

Ce projet combine plusieurs fonctionnalités autour d'une API FastAPI:

1. **Authentification sécurisée** - Système de login avec JWT stockés dans des cookies
2. **Base de données SQL** - Gestion de recettes de cuisine avec ingrédients et étapes
3. **Base de données MongoDB** - Analyse des populations des villes françaises
4. **Analyse de la loi de Benford** - Application aux images pour détecter les manipulations

## Fonctionnalités principales

- **API REST complète** avec documentation automatique (Swagger UI)
- **Système d'authentification** par mot de passe et tokens JWT
- **Scraping de données** depuis Marmiton pour alimenter la base SQL
- **Visualisation de données** avec Matplotlib et affichage HTML
- **Tests automatisés** via notebooks Jupyter

## Structure du projet

- `main.py` - Point d'entrée de l'application FastAPI
- `auth.py` - Système d'authentification et middleware de sécurité
- `templates/` - Templates HTML pour l'interface utilisateur
- `notebooks/` - Notebooks Jupyter pour les tests et analyses:
  - `test.ipynb` - Tests des endpoints API
  - `sql_webscraping.ipynb` - Scraping et insertion des recettes
  - `mongodbville.ipynb` - Analyse des populations avec la loi de Benford

## Installation

1. Cloner le dépôt
2. Installer les dépendances: `pip install -r requirements.txt`
3. Configurer les variables d'environnement (voir `.env.example`)
4. Lancer l'application: `uvicorn main:app --reload`

## Utilisation

1. Accéder à l'interface web: http://localhost:8000
2. Se connecter avec le mot de passe (par défaut: "lapin")
3. Explorer les différentes fonctionnalités via l'interface ou les notebooks

## API Endpoints

- **Authentication**: `/login`, `/logout`
- **Recettes SQL**: 
  - `/recipes/` - Liste toutes les recettes
  - `/recipe/{id}/steps` - Étapes d'une recette
  - `/recipe/{id}/ingredients` - Ingrédients d'une recette
- **MongoDB Villes**:
  - `/mongodb/insert` - Ajoute une ville
  - `/mongodb/update/{nom}` - Met à jour une ville
  - `/mongodb/delete/{nom}` - Supprime une ville
- **Analyse Benford**:
  - `/benford/` - Analyse la loi de Benford sur des images

## Licence

Ce projet est sous licence MIT.