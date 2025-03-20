# Application de Suivi Documentaire

## Description
Un système de gestion documentaire simple et intuitif développé en Python avec Streamlit et SQLite.
Choix d'une approche par dataframe statique pour faciliter l'hébergement sur Streamlit mais possible avec SQLite

## Fonctionnalités

### Page d'Accueil
- Vue d'ensemble des documents enregistrés
- Affichage des détails : ID, nom, catégorie, tags, date d'ajout

### Ajouter un Document
- Saisissez les informations du document
- Catégorisez et étiquetez vos documents
- Ajoutez une description facultative

### Rechercher des Documents
- Filtrez par catégorie
- Recherchez par étiquettes

### Gérer les Documents
- Modifiez le statut des documents
- Options : Actif, Archivé, Supprimé

## Structure du Projet
- `app.py`: Application Streamlit principale
- `load_test_documents.py`: Script de chargement des données
- `sample_documents.csv`: Fichier de données de test
- `document_tracking.db`: Base de données SQLite (générée automatiquement)

## Améliorations Futures
- Authentification des utilisateurs
- Recherche full-text
- Gestion des fichiers physiques
- Rapports et analyses avancées


## Licence
 MIT
