import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import random
from datetime import datetime, timezone

@st.cache_data
def load_documents():
    """
    Charge les documents depuis le CSV
    """
    import csv
    
    documents = []
    with open('sample_documents.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        upload_date = datetime.now(timezone.utc)

        for row in csv_reader:
            # Générer des tags et un statut
            generated_tags = generate_tags(row['category'], row['description'])
            category_status = assign_category_status(row['category'])
            
            documents.append({
                'filename': row['filename'],
                'filepath': row['filepath'],
                'upload_date': upload_date,
                'category': row['category'],
                'tags': generated_tags,
                'description': row['description'],
                'status': category_status
            })
    
    return pd.DataFrame(documents)

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

    # Commencer avec les tags de base de la catégorie
    tags = set(random.sample(CATEGORY_TAGS.get(category, []), 3))
    
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
            tags.update(random.sample(related_tags, min(2, len(related_tags))))
    
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

def get_documents_dataframe(search_category=None, search_tags=None):
    """
    Récupère les documents sous forme de DataFrame avec filtres optionnels
    """
    df = load_documents()
    
    # Filtres
    if search_category:
        df = df[df['category'] == search_category]
    
    if search_tags:
        df = df[df['tags'].str.contains(search_tags, case=False, na=False)]
    
    return df

def add_document(filename, filepath, category, tags, description):
    """
    Ajoute un nouveau document (simulé dans un DataFrame en mémoire)
    """
    # Charger les documents existants
    documents_df = load_documents()
    
    # Générer les tags et le statut
    generated_tags = generate_tags(category, description)
    category_status = assign_category_status(category)
    
    # Créer une nouvelle entrée
    new_document = pd.DataFrame({
        'filename': [filename],
        'filepath': [filepath],
        'upload_date': [datetime.now(timezone.utc)],
        'category': [category],
        'tags': [generated_tags],
        'description': [description],
        'status': [category_status]
    })
    
    # Concaténer avec les documents existants
    updated_documents = pd.concat([documents_df, new_document], ignore_index=True)
    
    return updated_documents

def create_category_donut_chart(df):
    """
    Crée un graphique en donut pour les catégories
    """
    category_counts = df['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values, 
        names=category_counts.index, 
        title='Répartition des Documents par Catégorie',
        hole=0.3,  # Crée un effet donut
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_status_bar_chart(df):
    """
    Crée un graphique à barres pour les statuts
    """
    status_counts = df['status'].value_counts()
    
    fig = px.bar(
        x=status_counts.index, 
        y=status_counts.values, 
        title='Nombre de Documents par Statut',
        labels={'x': 'Statut', 'y': 'Nombre de Documents'},
        color=status_counts.index,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    return fig

def create_tags_bar_chart(df):
    """
    Crée un graphique à barres pour les tags les plus fréquents
    avec une gestion améliorée des tags
    """
    # Séparer et compter les tags
    # Utiliser str.split avec expand=True pour gérer correctement les virgules
    all_tags = df['tags'].str.split(',', expand=True).stack()
    
    # Nettoyer les tags (supprimer les espaces, convertir en minuscules)
    all_tags = all_tags.str.strip().str.lower()
    
    # Compter les occurrences de tags
    tag_counts = all_tags.value_counts()
    
    # Filtrer pour n'afficher que les tags les plus pertinents (top 10)
    top_tags = tag_counts.head(10)
    
    # Créer le graphique avec Plotly
    fig = px.bar(
        x=top_tags.index, 
        y=top_tags.values,
        title='Top 10 des Tags',
        labels={'x': 'Tags', 'y': 'Fréquence'},
        color=top_tags.index,  # Colorer par tag
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Personnaliser la mise en page
    fig.update_layout(
        xaxis_title='Tags',
        yaxis_title='Nombre de Documents',
        xaxis_tickangle=-45  # Incliner les étiquettes pour une meilleure lisibilité
    )
    
    return fig

def main():
    # Configuration de la page pour utiliser toute la largeur
    st.set_page_config(layout="wide")

    # Titre de l'application
    st.title("🗂️ Système de Suivi Documentaire")
    
    # Sous-titre
    st.markdown("### 📋 Un prototype de gestion documentaire")

    # Menu principal
    action = st.radio("Choisissez une action", [
        "Ajouter un Document", 
        "Rechercher des Documents", 
        "Gérer les Documents"
    ], horizontal=True)

    # Créer trois colonnes larges
    col_home, col_action, col_viz = st.columns([2, 1, 1])

    # Récupérer les documents
    documents_df = get_documents_dataframe()

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
                submit_button = st.form_submit_button(label='Ajouter')

                if submit_button:
                    if filename and filepath:
                        try:
                            # Ajouter le document
                            documents_df = add_document(
                                filename, filepath, category, tags, description
                            )
                            st.success("Document ajouté avec succès!")
                            st.rerun()
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
                    documents_df = get_documents_dataframe(
                        search_category or None, 
                        search_tags or None
                    )

                    if not documents_df.empty:
                        st.dataframe(documents_df, use_container_width=True)
                    else:
                        st.warning("Aucun document trouvé.")

        elif action == "Gérer les Documents":
            for _, doc in documents_df.iterrows():
                with st.expander(f"ID: {doc.name} - {doc['filename']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Nom du Fichier:** {doc['filename']}")
                        st.write(f"**Chemin:** {doc['filepath']}")
                        st.write(f"**Catégorie:** {doc['category']}")
                        st.write(f"**Tags:** {doc['tags']}")
                        st.write(f"**Description:** {doc['description']}")
                    
                    with col2:
                        st.write(f"**Date d'ajout:** {doc['upload_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        new_status = st.selectbox(
                            "Statut", 
                            ["Actif", "Archivé", "Supprimé"], 
                            key=f"status_{doc.name}",
                            index=["Actif", "Archivé", "Supprimé"].index(doc['status'])
                        )
                        
                        if st.button(f"Mettre à jour", key=f"update_{doc.name}"):
                            # Mettre à jour le statut du document
                            documents_df.loc[doc.name, 'status'] = new_status
                            st.success(f"Statut de {doc['filename']} mis à jour à {new_status}")
                            st.rerun()

    # Colonne de Visualisation
    with col_viz:
        st.header("📊 Visualisations")
        
        # Créer des onglets pour différentes visualisations
        tab1, tab2, tab3 = st.tabs([
            "Catégories", 
            "Statuts", 
            "Tags"
        ])

        with tab1:
            # Graphique des catégories (Donut Chart)
            fig_categories = create_category_donut_chart(documents_df)
            st.plotly_chart(fig_categories, use_container_width=True)

        with tab2:
            # Graphique des statuts
            fig_status = create_status_bar_chart(documents_df)
            st.plotly_chart(fig_status, use_container_width=True)

        with tab3:
            # Distribution des tags
            fig_tags = create_tags_bar_chart(documents_df)
            st.plotly_chart(fig_tags, use_container_width=True)

if __name__ == "__main__":
    main()