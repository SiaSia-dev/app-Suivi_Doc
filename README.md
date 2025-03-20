# Application de Suivi Documentaire

## Description
Un système de gestion documentaire simple et intuitif développé en Python avec Streamlit et SQLite.

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

## Dépannage
- Assurez-vous que Python et Streamlit sont correctement installés
- Vérifiez que tous les fichiers sont dans le même répertoire
- En cas d'erreur, recréez l'environnement virtuel

## Licence
 MIT
