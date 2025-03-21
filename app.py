import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import random
from datetime import datetime, timedelta, timezone
import os

# Nom du fichier CSV pour stocker les documents
DOCUMENTS_CSV = 'sample_documents.csv'

@st.cache_data
def load_documents():
    """
    Charge les documents depuis le CSV, crée un fichier vide s'il n'existe pas
    """
    # Colonnes requises pour l'application
    required_columns = ['filename', 'filepath', 'upload_date', 'category', 'tags', 'description', 'status']
    
    try:
        # Vérifier si le fichier existe
        if os.path.exists(DOCUMENTS_CSV):
            # Vérifier si le fichier est vide
            if os.path.getsize(DOCUMENTS_CSV) == 0:
                # Si le fichier est vide, créer un fichier CSV correctement formaté
                empty_df = pd.DataFrame(columns=required_columns)
                empty_df.to_csv(DOCUMENTS_CSV, index=False)
                return empty_df
            
            # Lire le fichier CSV existant
            df = pd.read_csv(DOCUMENTS_CSV)
            
            # Vérifier que toutes les colonnes requises sont présentes
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                st.warning(f"Colonnes manquantes dans le CSV: {', '.join(missing_columns)}")
                # Ajouter les colonnes manquantes
                for col in missing_columns:
                    df[col] = ''  # Valeur par défaut vide
                # Sauvegarder le fichier avec les colonnes ajoutées
                df.to_csv(DOCUMENTS_CSV, index=False)
            
            # Convertir la date de string à datetime
            if 'upload_date' in df.columns:
                df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')
                
            # Vérifier si la colonne tags contient des valeurs NaN ou float, et les convertir en chaînes vides
            if 'tags' in df.columns:
                df['tags'] = df['tags'].apply(lambda x: '' if pd.isna(x) else str(x))
                # Convertir les valeurs numériques en chaînes vides (comme '0.0' ou 'nan')
                df['tags'] = df['tags'].apply(lambda x: '' if x == '0.0' or x == 'nan' or x == 'NaN' else x)
                
            # Générer des tags si la colonne tags est vide
            for idx, row in df.iterrows():
                if pd.isna(row['tags']) or row['tags'] == '':
                    if not pd.isna(row['category']) and not pd.isna(row['description']):
                        df.at[idx, 'tags'] = generate_tags(row['category'], row['description'])
            
            # Générer des statuts si la colonne status est vide
            for idx, row in df.iterrows():
                if pd.isna(row['status']) or row['status'] == '':
                    if not pd.isna(row['category']):
                        df.at[idx, 'status'] = assign_category_status(row['category'])
            
            # Sauvegarder les modifications (tags et statuts générés)
            df.to_csv(DOCUMENTS_CSV, index=False)
            
            return df
        else:
            # Créer un DataFrame vide avec les colonnes requises
            empty_df = pd.DataFrame(columns=required_columns)
            
            # Sauvegarder le CSV vide pour les futures utilisations
            empty_df.to_csv(DOCUMENTS_CSV, index=False)
            
            return empty_df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des documents: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame(columns=required_columns)

def generate_random_date(days_range=0):
    """
    Génère la date du jour plutôt qu'une date aléatoire
    
    Args:
        days_range (int): Paramètre conservé pour compatibilité, non utilisé
        
    Returns:
        datetime: Date actuelle avec timezone UTC
    """
    # Date actuelle
    current_date = datetime.now(timezone.utc)
    return current_date

def generate_tags(category, description):
    """
    Génère des tags basés sur la catégorie et la description
    """
    # Vérifier si la catégorie ou la description est None ou vide
    if not category or not description:
        return 'non_classifié'
    
    # S'assurer que la description est une chaîne de caractères
    if not isinstance(description, str):
        description = str(description)
        
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
        ],
        'Autre': [
            'document', 'information', 'données', 'archive',
            'divers', 'indéfini', 'classement', 'référence',
            'documentation', 'support'
        ]
    }

    # S'assurer que la catégorie existe dans le dictionnaire
    if category not in CATEGORY_TAGS:
        category = 'Autre'
    
    # Commencer avec les tags de base de la catégorie (s'assurer que la liste n'est pas vide)
    available_tags = CATEGORY_TAGS.get(category, ['document'])
    
    # S'assurer que nous ne demandons pas plus de tags que ceux disponibles
    num_tags = min(3, len(available_tags))
    tags = set(random.sample(available_tags, num_tags))
    
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
            # S'assurer que nous ne demandons pas plus de tags que ceux disponibles
            num_related_tags = min(2, len(related_tags))
            if num_related_tags > 0:  # Vérifier qu'il y a des tags à ajouter
                tags.update(random.sample(related_tags, num_related_tags))
    
    # Ajouter l'année si présente dans la description
    years = [str(year) for year in range(2020, 2025)]
    for year in years:
        if year in description:
            tags.add(year)
    
    # Ajouter des tags spécifiques à la catégorie
    if category == 'Administratif':
        if 'finances' in description.lower():
            tags.update(['comptabilité', 'budget'])
        if 'maintenance' in description.lower():
            tags.update(['technique', 'infrastructure'])
    
    elif category == 'Projet':
        if 'innovation' in description.lower():
            tags.update(['R&D', 'développement'])
        if 'client' in description.lower():
            tags.update(['satisfaction', 'relation_client'])
    
    elif category == 'Personnel':
        if 'recrutement' in description.lower():
            tags.update(['CV', 'competences'])
        if 'formation' in description.lower():
            tags.update(['developpement', 'integration'])
    
    # Limiter à 5 tags uniques
    unique_tags = list(tags)[:5]
    
    # S'assurer qu'il y a au moins un tag
    if not unique_tags:
        unique_tags = ['non_classifié']
    
    return ','.join(unique_tags)

def assign_category_status(category):
    """
    Génère un statut basé sur la catégorie pour une distribution plus réaliste
    """
    status_distribution = {
        'Administratif': ['Actif', 'Actif', 'Archivé', 'Supprimé'],
        'Projet': ['Actif', 'Actif', 'Actif', 'Archivé', 'Supprimé'],
        'Personnel': ['Actif', 'Archivé', 'Archivé', 'Supprimé'],
        'Autre': ['Actif', 'Actif', 'Archivé', 'Supprimé']
    }
    # S'assurer que la catégorie n'est pas None
    if not category:
        return 'Actif'
        
    return random.choice(status_distribution.get(category, ['Actif', 'Archivé', 'Supprimé']))

def get_documents_dataframe(search_category=None, search_tags=None):
    """
    Récupère les documents sous forme de DataFrame avec filtres optionnels
    """
    df = load_documents()
    
    # Si le DataFrame est vide, retournez-le tel quel
    if df.empty:
        return df
    
    # Filtres
    if search_category:
        df = df[df['category'] == search_category]
    
    if search_tags:
        df = df[df['tags'].str.contains(search_tags, case=False, na=False)]
    
    return df

def create_category_donut_chart(df):
    """
    Crée un graphique en donut pour les catégories avec gestion des filtres
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Aucune donnée disponible pour les catégories")
        return fig
    
    if 'category' not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="Colonne 'category' manquante dans les données")
        return fig
    
    # Nettoyer et gérer les valeurs nulles ou vides
    df = df.copy()
    df['category'] = df['category'].fillna('Non défini')
    df.loc[df['category'] == '', 'category'] = 'Non défini'
    
    category_counts = df['category'].value_counts()
    
    # Créer des étiquettes personnalisées avec pourcentages
    total = category_counts.sum()
    labels = [f"{cat} ({count}) - {count/total*100:.1f}%" for cat, count in category_counts.items()]
    
    fig = px.pie(
        values=category_counts.values, 
        names=labels,  # Utiliser les étiquettes personnalisées
        title='Répartition des Documents par Catégorie',
        hole=0.3,  # Crée un effet donut
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent')
    
    # Personnaliser la mise en page
    fig.update_layout(
        title_x=0.5,  # Centrer le titre
        legend_title_text='Catégories',
        annotations=[dict(text=f'Total: {total} documents', x=0.5, y=-0.1, showarrow=False)]
    )
    
    return fig

def create_status_bar_chart(df):
    """
    Crée un graphique à barres pour les statuts avec gestion des filtres
    """
    if df.empty or 'status' not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="Aucune donnée disponible pour les statuts")
        return fig
    
    # Nettoyer et gérer les valeurs nulles ou vides
    df = df.copy()
    df['status'] = df['status'].fillna('Non défini')
    df.loc[df['status'] == '', 'status'] = 'Non défini'
    
    status_counts = df['status'].value_counts()
    
    # Créer des étiquettes personnalisées avec pourcentages
    total = status_counts.sum()
    labels = [f"{status} ({count}) - {count/total*100:.1f}%" for status, count in status_counts.items()]
    
    fig = px.bar(
        x=labels, 
        y=status_counts.values, 
        title='Nombre de Documents par Statut',
        labels={'x': 'Statut', 'y': 'Nombre de Documents'},
        color=status_counts.index,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Personnaliser la mise en page
    fig.update_layout(
        title_x=0.5,  # Centrer le titre
        xaxis_title='Statuts',
        yaxis_title='Nombre de Documents',
        xaxis_tickangle=-45,  # Incliner les étiquettes
        annotations=[dict(text=f'Total: {total} documents', x=0.5, y=-0.1, showarrow=False)]
    )
    
    return fig

def create_tags_bar_chart(df):
    """
    Crée un graphique à barres pour les tags les plus fréquents avec gestion des filtres
    """
    if df.empty or 'tags' not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="Aucune donnée disponible pour les tags")
        return fig
    
    # Séparer et compter les tags
    all_tags = df['tags'].str.split(',', expand=True).stack()
    
    if all_tags.empty:
        fig = go.Figure()
        fig.update_layout(title="Aucun tag disponible")
        return fig
    
    # Nettoyer les tags (supprimer les espaces, convertir en minuscules)
    all_tags = all_tags.str.strip().str.lower()
    
    # Compter les occurrences de tags
    tag_counts = all_tags.value_counts()
    
# Filtrer pour n'afficher que les tags les plus pertinents (top 10)
    top_tags = tag_counts.head(10)
    
    # Créer des étiquettes personnalisées avec pourcentages
    total = top_tags.sum()
    labels = [f"{tag} ({count}) - {count/total*100:.1f}%" for tag, count in top_tags.items()]
    
    # Créer le graphique avec Plotly
    fig = px.bar(
        x=labels, 
        y=top_tags.values,
        title='Top 10 des Tags',
        labels={'x': 'Tags', 'y': 'Fréquence'},
        color=top_tags.index,  # Colorer par tag
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Personnaliser la mise en page
    fig.update_layout(
        title_x=0.5,  # Centrer le titre
        xaxis_title='Tags',
        yaxis_title='Nombre de Documents',
        xaxis_tickangle=-45,  # Incliner les étiquettes pour une meilleure lisibilité
        annotations=[dict(text=f'Total des documents analysés: {total}', x=0.5, y=-0.1, showarrow=False)]
    )
    
    return fig

def add_document(filename, filepath, category, tags, description, random_date=False):
    """
    Ajoute un nouveau document au CSV et retourne le DataFrame mis à jour
    
    Args:
        filename (str): Nom du fichier
        filepath (str): Chemin du fichier
        category (str): Catégorie du document
        tags (str): Tags du document (si vide, seront générés automatiquement)
        description (str): Description du document
        random_date (bool): Si True, génère une date aléatoire au lieu de la date actuelle
    """
    # Charger les documents existants
    documents_df = load_documents()
    
    # Toujours générer les tags automatiquement si l'utilisateur n'en a pas spécifié
    # Cela garantit que l'attribution automatique fonctionne comme prévu
    generated_tags = tags
    if not tags:
        generated_tags = generate_tags(category, description)
    
    # Toujours générer un statut basé sur la catégorie
    category_status = assign_category_status(category)
    
    # Générer une date d'upload (aléatoire ou timestamp actuel)
    if random_date:
        upload_date = generate_random_date()
    else:
        upload_date = datetime.now(timezone.utc)
    
    # Créer une nouvelle entrée
    new_document = pd.DataFrame({
        'filename': [filename],
        'filepath': [filepath],
        'upload_date': [upload_date],
        'category': [category],
        'tags': [generated_tags],
        'description': [description],
        'status': [category_status]
    })
    
    # Concaténer avec les documents existants
    updated_documents = pd.concat([documents_df, new_document], ignore_index=True)
    
    # Sauvegarder dans le fichier CSV
    try:
        updated_documents.to_csv(DOCUMENTS_CSV, index=False)
        st.session_state['documents_updated'] = True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde des documents: {e}")
    
    return updated_documents

def update_document_status(document_index, new_status):
    """
    Met à jour le statut d'un document et sauvegarde les changements
    """
    # Charger les documents existants
    documents_df = load_documents()
    
    # Vérifier si l'index existe
    if document_index in documents_df.index:
        # Mettre à jour le statut
        documents_df.loc[document_index, 'status'] = new_status
        
        # Sauvegarder les modifications
        try:
            documents_df.to_csv(DOCUMENTS_CSV, index=False)
            # Signaler que les documents ont été mis à jour pour recharger le cache
            st.session_state['documents_updated'] = True
            return True
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde des modifications: {e}")
            return False
    else:
        st.warning(f"Document avec index {document_index} non trouvé.")
        return False

def delete_document(document_index):
    """
    Supprime un document du DataFrame et met à jour le fichier CSV
    
    Args:
        document_index (int): Index du document à supprimer
    
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    # Charger les documents existants
    documents_df = load_documents()
    
    try:
        # Vérifier que l'index existe
        if document_index in documents_df.index:
            # Supprimer la ligne avec cet index
            updated_df = documents_df.drop(document_index)
            
            # Réinitialiser les index
            updated_df = updated_df.reset_index(drop=True)
            
            # Sauvegarder le DataFrame mis à jour
            updated_df.to_csv(DOCUMENTS_CSV, index=False)
            
            # Signaler que les documents ont été mis à jour pour recharger le cache
            st.session_state['documents_updated'] = True
            
            return True
        else:
            st.warning(f"Document avec index {document_index} non trouvé.")
            return False
    except Exception as e:
        st.error(f"Erreur lors de la suppression du document: {e}")
        return False

def delete_multiple_documents(document_indices):
    """
    Supprime plusieurs documents du DataFrame et met à jour le fichier CSV
    
    Args:
        document_indices (list): Liste des indices des documents à supprimer
    
    Returns:
        tuple: (bool, int) - Succès de l'opération et nombre de documents supprimés
    """
    if not document_indices:
        return False, 0
        
    # Charger les documents existants
    documents_df = load_documents()
    
    try:
        # Vérifier que les indices existent
        valid_indices = [idx for idx in document_indices if idx in documents_df.index]
        
        if not valid_indices:
            st.warning("Aucun document valide à supprimer.")
            return False, 0
        
        # Supprimer les lignes avec ces indices
        updated_df = documents_df.drop(valid_indices)
        
        # Réinitialiser les index
        updated_df = updated_df.reset_index(drop=True)
        
        # Sauvegarder le DataFrame mis à jour
        updated_df.to_csv(DOCUMENTS_CSV, index=False)
        
        # Signaler que les documents ont été mis à jour pour recharger le cache
        st.session_state['documents_updated'] = True
        
        return True, len(valid_indices)
    except Exception as e:
        st.error(f"Erreur lors de la suppression des documents: {e}")
        return False, 0

def main():
    # Configuration de la page pour utiliser toute la largeur
    st.set_page_config(layout="wide")

    # Initialiser l'état de session pour suivre les mises à jour
    if 'documents_updated' not in st.session_state:
        st.session_state['documents_updated'] = False

    # Titre de l'application
    st.title("🗂️ Système de Suivi Documentaire")
    
    # Sous-titre
    st.markdown("### 📋 Un prototype de gestion documentaire")

    # Menu principal
    action = st.radio("Choisissez une action", [
        "Ajouter un Document", 
        "Rechercher des Documents", 
        "Gérer les Documents",
        "Régénérer les Tags",
        "Supprimer des Documents"
    ], horizontal=True)

    # Créer trois colonnes larges
    col_home, col_action, col_viz = st.columns([2, 1, 1])

    # Si les documents ont été mis à jour, recharger le cache
    if st.session_state.get('documents_updated', False):
        # Vider le cache pour forcer le rechargement des données
        st.cache_data.clear()
        st.session_state['documents_updated'] = False

    # Récupérer les documents et vérifier si le fichier CSV existe
    try:
        if not os.path.exists(DOCUMENTS_CSV):
            st.info(f"Le fichier {DOCUMENTS_CSV} n'existe pas encore. Il sera créé lorsque vous ajouterez un document.")
            
            # Créer un fichier vide si nécessaire
            empty_df = pd.DataFrame(columns=['filename', 'filepath', 'upload_date', 'category', 'tags', 'description', 'status'])
            empty_df.to_csv(DOCUMENTS_CSV, index=False)
            
        documents_df = get_documents_dataframe()
    except Exception as e:
        st.error(f"Erreur lors du chargement des documents: {e}")
        # Créer un DataFrame vide en cas d'erreur
        documents_df = pd.DataFrame(columns=['filename', 'filepath', 'upload_date', 'category', 'tags', 'description', 'status'])

    # Colonne d'Accueil
    with col_home:
        st.header("📋 Liste des Documents")
        
        if not documents_df.empty:
            st.dataframe(documents_df, use_container_width=True)
        else:
            st.info("Aucun document n'a encore été ajouté.")

    # Colonne d'Action
    with col_action:
        st.header("🚀 Action")
        
        if action == "Ajouter un Document":
            with st.form(key='add_doc_form'):
                filename = st.text_input("Nom du Fichier")
                filepath = st.text_input("Chemin du Fichier")
                category = st.selectbox("Catégorie", 
                    ["Administratif", "Projet", "Personnel", "Autre"])
                tags = st.text_input("Étiquettes (séparées par des virgules)")
                description = st.text_area("Description")
                random_date = st.checkbox("Utiliser une date aléatoire", value=True, 
                                         help="Si coché, la date actuelle sera utilisée comme date d'ajout.")
                submit_button = st.form_submit_button(label='Ajouter')

                if submit_button:
                    if filename and filepath:
                        try:
                            # Ajouter le document avec date aléatoire si demandé
                            add_document(
                                filename, filepath, category, tags, description, random_date
                            )
                            st.success("Document ajouté avec succès!")
                            st.experimental_rerun()  # Force le rechargement complet de l'application
                        except Exception as e:
                            st.error(f"Erreur lors de l'ajout du document : {e}")
                    else:
                        st.error("Veuillez remplir au moins le nom et le chemin du fichier")

        elif action == "Rechercher des Documents":
            with st.form(key='search_doc_form'):
                search_category = st.selectbox("Filtrer par Catégorie", 
                    ["", "Administratif", "Projet", "Personnel", "Autre"])
                search_tags = st.text_input("Rechercher par Étiquettes")
                search_button = st.form_submit_button(label='Rechercher')

                if search_button:
                    # Récupérer les documents filtrés
                    filtered_df = get_documents_dataframe(
                        search_category or None, 
                        search_tags or None
                    )

                    if not filtered_df.empty:
                        st.dataframe(filtered_df, use_container_width=True)
                    else:
                        st.warning("Aucun document trouvé.")

        # Le reste du code de la fonction main() reste similaire...

    # Colonne de Visualisation : Ajout des filtres
    with col_viz:
        st.header("📊 Visualisations")
        
        # Filtres pour les visualisations
        st.write("**Filtres de Visualisation**")
        
        # Filtres par catégorie et statut
        filter_category_viz = st.selectbox(
            "Filtrer par Catégorie", 
            ["Toutes"] + sorted(documents_df['category'].unique().tolist())
        )
        
        filter_status_viz = st.selectbox(
            "Filtrer par Statut", 
            ["Tous"] + sorted(documents_df['status'].unique().tolist())
        )
        
        # Appliquer les filtres au DataFrame
        filtered_df = documents_df.copy()
        if filter_category_viz != "Toutes":
            filtered_df = filtered_df[filtered_df['category'] == filter_category_viz]
        if filter_status_viz != "Tous":
            filtered_df = filtered_df[filtered_df['status'] == filter_status_viz]
        
        # Créer des onglets pour différentes visualisations
        tab1, tab2, tab3 = st.tabs([
            "Catégories", 
            "Statuts", 
            "Tags"
        ])

        with tab1:
            # Graphique des catégories (Donut Chart)
            fig_categories = create_category_donut_chart(filtered_df)
            st.plotly_chart(fig_categories, use_container_width=True)

        with tab2:
            # Graphique des statuts
            fig_status = create_status_bar_chart(filtered_df)
            st.plotly_chart(fig_status, use_container_width=True)

        with tab3:
            # Distribution des tags
            fig_tags = create_tags_bar_chart(filtered_df)
            st.plotly_chart(fig_tags, use_container_width=True)

if __name__ == "__main__":
    main()    