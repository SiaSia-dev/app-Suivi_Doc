import pandas as pd

# Charger le fichier CSV
csv_file = 'sample_documents.csv'
df = pd.read_csv(csv_file)

# Afficher les premières lignes pour vérifier
print("Avant nettoyage:")
print(df.head())

# Vider la colonne 'tags'
df['tags'] = ''

# Sauvegarder le fichier modifié
df.to_csv(csv_file, index=False)

print("\nAprès nettoyage:")
print(df.head())
print(f"\nLe fichier {csv_file} a été modifié avec succès. Les tags ont été vidés.")
