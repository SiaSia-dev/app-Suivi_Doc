import streamlit as st
import sqlite3
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

def adapt_datetime(val):
    """
    Convertit un objet datetime en chaîne ISO formatée
    """
    return val.isoformat()

def convert_datetime(val):
    """
    Convertit une chaîne ISO en objet datetime
    """
    return datetime.fromisoformat(val.decode())

# Enregistrer les adaptateurs personnalisés
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)

def get_documents_dataframe(search_category=None, search_tags=None):
    """
    Récupère les documents sous forme de DataFrame avec filtres optionnels
    """
    conn = sqlite3.connect('document_tracking.db', detect_types=sqlite3.PARSE_DECLTYPES)
    
    # Construction de la requête dynamique
    query = "SELECT * FROM documents WHERE 1=1"
    params = []
    
    if search_category:
        query += " AND category = ?"
        params.append(search_category)
    
    if search_tags:
        query += " AND tags LIKE ?"
        params.append(f"%{search_tags}%")
    
    # Exécuter la requête
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

def create_category_pie_chart(df):
    """
    Crée un graphique à secteurs pour les catégories de documents
    """
    if df.empty:
        return None
    
    category_counts = df['category'].value_counts()
    fig = px.pie(
        values=category_counts.values, 
        names=category_counts.index, 
        title='Répartition des Documents par Catégorie',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_status_bar_chart(df):
    """
    Crée un graphique à barres pour les statuts des documents
    """
    if df.empty:
        return None
    
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

def create_tags_wordcloud(df):
    """
    Crée un graphique de distribution des tags
    """
    if df.empty:
        return None
    
    all_tags = df['tags'].str.split(',').explode()
    tag_counts = all_tags.str.strip().value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=tag_counts.index, 
        y=tag_counts.values,
        marker_color=px.colors.qualitative.Pastel
    )])
    fig.update_layout(
        title='Distribution des Tags',
        xaxis_title='Tags',
        yaxis_title='Fréquence',
        xaxis_tickangle=-45
    )
    return fig

def create_timeline_chart(df):
    """
    Crée une timeline des documents
    """
    if df.empty:
        return None
    
    df['upload_date'] = pd.to_datetime(df['upload_date'])
    monthly_docs = df.groupby(pd.Grouper(key='upload_date', freq='ME')).size()
    
    fig = go.Figure(data=[go.Scatter(
        x=monthly_docs.index, 
        y=monthly_docs.values,
        mode='lines+markers',
        line=dict(color='rgba(0, 128, 255, 0.7)'),
        marker=dict(size=10, color='rgba(0, 128, 255, 0.7)')
    )])
    fig.update_layout(
        title='Chronologie des Documents',
        xaxis_title='Date',
        yaxis_title='Nombre de Documents',
        template='plotly_white'
    )
    return fig

def main():
    # Configuration de la page pour utiliser toute la largeur
    st.set_page_config(layout="wide")

    # Titre de l'application
    st.title("🗂️ Système de Suivi Documentaire")
    # sous-title
    st.subheader("Prototype d'application pour suivre et gérer les documents")

    # Menu principal
    action = st.radio("Choisissez une action", [
        "Ajouter un Document", 
        "Rechercher des Documents", 
        "Gérer les Documents"
    ], horizontal=True)

    # Créer trois colonnes larges
    col_home, col_action, col_viz = st.columns([2, 1, 1])

    # Variables pour stocker les filtres de recherche
    search_category = None
    search_tags = None

    # Colonne d'Accueil
    with col_home:
        st.header("📋 Liste des Documents")
        
        # Récupérer les documents (initialement tous)
        documents_df = get_documents_dataframe()
        
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
                            conn = sqlite3.connect('document_tracking.db', detect_types=sqlite3.PARSE_DECLTYPES)
                            cursor = conn.cursor()
                            
                            upload_date = datetime.now()
                            
                            cursor.execute('''
                            INSERT INTO documents 
                            (filename, filepath, upload_date, category, tags, description) 
                            VALUES (?, ?, ?, ?, ?, ?)
                            ''', (filename, filepath, upload_date, category, tags, description))
                            
                            conn.commit()
                            conn.close()
                            
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
            conn = sqlite3.connect('document_tracking.db', detect_types=sqlite3.PARSE_DECLTYPES)
            documents = pd.read_sql_query('SELECT * FROM documents', conn)
            conn.close()
            
            for _, doc in documents.iterrows():
                with st.expander(f"ID: {doc['id']} - {doc['filename']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Nom du Fichier:** {doc['filename']}")
                        st.write(f"**Chemin:** {doc['filepath']}")
                        st.write(f"**Catégorie:** {doc['category']}")
                        st.write(f"**Tags:** {doc['tags']}")
                        st.write(f"**Description:** {doc['description'] or 'Aucune description'}")
                    
                    with col2:
                        st.write(f"**Date d'ajout:** {pd.to_datetime(doc['upload_date']).strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        new_status = st.selectbox(
                            "Statut", 
                            ["Actif", "Archivé", "Supprimé"], 
                            key=f"status_{doc['id']}",
                            index=["Actif", "Archivé", "Supprimé"].index(doc['status'])
                        )
                        
                        if st.button(f"Mettre à jour", key=f"update_{doc['id']}"):
                            conn = sqlite3.connect('document_tracking.db', detect_types=sqlite3.PARSE_DECLTYPES)
                            cursor = conn.cursor()
                            
                            cursor.execute('''
                            UPDATE documents 
                            SET status = ? 
                            WHERE id = ?
                            ''', (new_status, doc['id']))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"Statut de {doc['filename']} mis à jour à {new_status}")
                            st.rerun()

    # Colonne de Visualisation
    with col_viz:
        st.header("📊 Visualisations")
        
        # Créer des onglets pour différentes visualisations
        tab1, tab2, tab3, tab4 = st.tabs([
            "Catégories", 
            "Statuts", 
            "Tags",
            "Chronologie"
        ])

        with tab1:
            fig_cat = create_category_pie_chart(documents_df)
            if fig_cat:
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Aucune donnée pour la visualisation")

        with tab2:
            fig_status = create_status_bar_chart(documents_df)
            if fig_status:
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("Aucune donnée pour la visualisation")

        with tab3:
            fig_tags = create_tags_wordcloud(documents_df)
            if fig_tags:
                st.plotly_chart(fig_tags, use_container_width=True)
            else:
                st.info("Aucune donnée pour la visualisation")

        with tab4:
            fig_timeline = create_timeline_chart(documents_df)
            if fig_timeline:
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("Aucune donnée pour la visualisation")

if __name__ == "__main__":
    main()
