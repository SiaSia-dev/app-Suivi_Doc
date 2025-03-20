import csv
import sqlite3
import random
from datetime import datetime, timezone

def adapt_datetime(val):
    """
    Convertit un objet datetime en chaîne ISO formatée
    """
    return val.isoformat()

def convert_datetime(val):
    """
    Convertit une chaîne ISO en objet datetime
    """
    # Gérer différents formats potentiels de date
    try:
        # Essayer de convertir directement
        return datetime.fromisoformat(val.decode())
    except Exception:
        try:
            # Essayer avec un format de secours
            return datetime.strptime(val.decode(), '%Y-%m-%d %H:%M:%S.%f%z')
        except Exception:
            # Utiliser la date courante si la conversion échoue
            return datetime.now(timezone.utc)

# Enregistrer les adaptateurs personnalisés
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)

def generate_tags(category, description):
    """
    Génère des tags basés sur la catégorie et la description
    """
    # Dictionnaire de tags par catégorie
    CATEGORY_TAGS = {
        'Administratif': [
            'administration', 'gestion', 'rapport', 'officiel', 
            'document_interne', 'conformité', 'archivage', 
            'politique', 'réglementation', 'procédure'
        ],
        'Projet': [
            'innovation', 'développement', 'stratégie', 'planification', 
            'R&D', 'client', 'proposition', 'cahier_des_charges', 
            'prototype', 'amélioration', 'objectifs'
        ],
        'Personnel': [
            'RH', 'recrutement', 'evaluation', 'competences', 
            'developpement_personnel', 'formation', 'integration', 
            'carriere', 'motivation', 'ressources_humaines'
        ]
    }

    # Tags de base pour la catégorie
    tags = random.sample(CATEGORY_TAGS.get(category, []), 3)
    
    # Mots-clés additionnels basés sur la description
    description_keywords = {
        'financier': ['finances', 'comptabilité', 'budget'],
        'stratégie': ['strategie', 'direction', 'management'],
        'maintenance': ['infrastructure', 'technique', 'systeme'],
        'client': ['satisfaction', 'relation_client', 'service'],
        'innovation': ['R&D', 'technologie', 'recherche'],
        'évaluation': ['performance', 'competences', 'developpement']
    }
    
    # Ajouter des tags basés sur la description
    for keyword, related_tags in description_keywords.items():
        if keyword in description.lower():
            tags.extend(random.sample(related_tags, min(2, len(related_tags))))
    
    # Ajouter l'année si présente dans la description
    years = [str(year) for year in range(2020, 2025)]
    for year in years:
        if year in description:
            tags.append(year)
    
    # Convertir en liste unique et limiter le nombre de tags
    unique_tags = list(set(tags))[:5]
    
    return ','.join(unique_tags)

def assign_category_status(category):
    """
    Génère un statut basé sur la catégorie pour une distribution plus réaliste
    """
    status_distribution = {
        'Administratif': ['Actif', 'Actif', 'Archivé', 'Supprimé'],
        'Projet': ['Actif', 'Actif', 'Actif', 'Archivé', 'Supprimé'],
        'Personnel': ['Actif', 'Archivé', 'Archivé', 'Supprimé']
    }
    return random.choice(status_distribution.get(category, ['Actif', 'Archivé', 'Supprimé']))

def load_test_documents(csv_file='sample_documents.csv', db_path='document_tracking.db'):
    """
    Charge les documents de test depuis un fichier CSV dans la base de données SQLite
    avec des tags et statuts générés dynamiquement
    """
    # Connexion à la base de données
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Créer la table si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        upload_date DATETIME NOT NULL,
        category TEXT,
        tags TEXT,
        description TEXT,
        status TEXT DEFAULT 'Actif'
    )
    ''')

    # Effacer les données existantes avant de charger (optionnel)
    cursor.execute('DELETE FROM documents')

    # Lire le fichier CSV
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        # Date d'upload courante
        upload_date = datetime.now(timezone.utc)

        # Insérer chaque document
        documents_added = 0
        for row in csv_reader:
            try:
                # Générer des tags basés sur la catégorie et la description
                generated_tags = generate_tags(row['category'], row['description'])
                
                # Générer un statut basé sur la catégorie
                category_status = assign_category_status(row['category'])
                
                cursor.execute('''
                INSERT INTO documents 
                (filename, filepath, upload_date, category, tags, description, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['filename'], 
                    row['filepath'], 
                    upload_date, 
                    row['category'], 
                    generated_tags, 
                    row['description'],
                    category_status
                ))
                documents_added += 1
            except Exception as e:
                print(f"Erreur lors de l'insertion du document {row['filename']}: {e}")

    # Valider et fermer la connexion
    conn.commit()
    
    # Vérifier le nombre de documents
    cursor.execute('SELECT COUNT(*) FROM documents')
    count = cursor.fetchone()[0]
    print(f"Nombre de documents chargés : {count}")
    
    conn.close()

    return documents_added

def display_loaded_documents(db_path='document_tracking.db'):
    """
    Affiche les documents chargés dans la base de données
    """
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Requête pour afficher les documents groupés par catégorie et statut
    cursor.execute('''
        SELECT category, status, COUNT(*) as count 
        FROM documents 
        GROUP BY category, status 
        ORDER BY category, status
    ''')
    category_status_summary = cursor.fetchall()
    
    print("\nRécapitulatif des documents par catégorie et statut :")
    for row in category_status_summary:
        print(f"Catégorie: {row[0]}, Statut: {row[1]}, Nombre: {row[2]}")
    
    print("\nDétails des documents :")
    cursor.execute('SELECT * FROM documents')
    documents = cursor.fetchall()
    
    for doc in documents:
        # Gérer la conversion de la date
        try:
            # Si c'est déjà un objet datetime
            date_str = doc[3].strftime('%Y-%m-%d %H:%M:%S')
        except (AttributeError, TypeError):
            # Si c'est une chaîne, essayer de la convertir
            try:
                date_obj = datetime.fromisoformat(doc[3])
                date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except:
                # Utiliser la chaîne telle quelle ou une valeur par défaut
                date_str = str(doc[3])
        
        print(f"""
ID: {doc[0]}
Nom du Fichier: {doc[1]}
Chemin: {doc[2]}
Date d'ajout: {date_str}
Catégorie: {doc[4]}
Tags: {doc[5]}
Description: {doc[6]}
Statut: {doc[7]}
""")
    
    conn.close()

if __name__ == "__main__":
    # Charger les documents
    loaded_count = load_test_documents()
    
    # Afficher les documents chargés
    display_loaded_documents()