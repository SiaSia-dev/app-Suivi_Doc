import pandas as pd
import random
from datetime import datetime, timedelta

# Fonction pour générer une date aléatoire dans les 6 derniers mois
def random_date(start_date, end_date):
    time_delta = end_date - start_date
    days_delta = time_delta.days
    random_days = random.randint(0, days_delta)
    return start_date + timedelta(days=random_days)

# Fonction pour assigner un statut basé sur la catégorie
def assign_category_status(category):
    """
    Génère un statut basé sur la catégorie pour une distribution plus réaliste
    """
    status_distribution = {
        'Administratif': ['Actif', 'Actif', 'Archivé', 'Supprimé'],
        'Projet': ['Actif', 'Actif', 'Actif', 'Archivé', 'Supprimé'],
        'Personnel': ['Actif', 'Archivé', 'Archivé', 'Supprimé'],
        'Autre': ['Actif', 'Actif', 'Archivé', 'Supprimé'],
    }
    return random.choice(status_distribution.get(category, ['Actif', 'Archivé', 'Supprimé']))

# Charger le fichier CSV
csv_file = 'sample_documents.csv'
df = pd.read_csv(csv_file)

# Afficher les premières lignes pour vérifier
print("Avant modification:")
print(df.head())

# Définir la plage de dates pour les dates d'upload (6 derniers mois)
end_date = datetime.now()
start_date = end_date - timedelta(days=180)  # Environ 6 mois

# Mettre à jour les colonnes
for idx, row in df.iterrows():
    # Générer un statut basé sur la catégorie
    if pd.isna(row['status']) or row['status'] == '':
        category = row['category'] if not pd.isna(row['category']) else 'Autre'
        df.at[idx, 'status'] = assign_category_status(category)
    
    # Générer une date d'upload aléatoire
    df.at[idx, 'upload_date'] = random_date(start_date, end_date).strftime('%Y-%m-%d %H:%M:%S')
    
    # S'assurer que la colonne tags est vide pour permettre la génération automatique
    df.at[idx, 'tags'] = ''

# Sauvegarder le fichier modifié
df.to_csv(csv_file, index=False)

print("\nAprès modification:")
print(df.head())
print(f"\nLe fichier {csv_file} a été modifié avec succès.")
print("- Les statuts ont été attribués aléatoirement en fonction de la catégorie")
print("- Les dates d'upload ont été générées aléatoirement sur les 6 derniers mois")
print("- Les tags ont été vidés pour permettre la génération automatique")
