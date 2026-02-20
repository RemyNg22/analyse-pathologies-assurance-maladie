import streamlit as st
from core.stats_pandas import charger_effectifs
from pages.Resume_Global import resume_global, page_resume_global
from pages.Analyse_Pathologies import analyse_pathologie
from pages.Analyse_territoriale import analyse_territoriale
from pages.Analyse_temporelle import analyse_temporelle
from pages.Anomalies import anomalies

"""
Application principale du dashboard d'analyse des pathologies.

Rôle :
- Charger les données
- Gérer la navigation entre les pages (Veuillez utiliser le menu déroulant et non les pages de la barre latérale)
- Centraliser les sélections utilisateur (sidebar)
- Appeler les fonctions d'analyse

"""


st.set_page_config(page_title="Dashboard Pathologies", layout="wide")

# Chargement des données
@st.cache_data
def load_data():
    return charger_effectifs()

df = load_data()

# Sidebar : sélection de la page
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choisir une page",
    [
        "Résumé global",
        "Analyse par pathologie",
        "Analyse territoriale",
        "Analyse temporelle",
        "Anomalies"
    ]
)

# Sidebar : sélection pathologie
pathologie = None
if page != "Résumé global":
    pathologie = st.sidebar.selectbox("Choisir une pathologie", sorted(df["pathologie"].unique()))

st.sidebar.divider()
st.sidebar.caption("Dashboard d'analyse des pathologies")


# Navigation
if page == "Résumé global":
    resume_global(df)
    page_resume_global(df)

elif page == "Analyse par pathologie":
    analyse_pathologie(df, pathologie)

elif page == "Analyse territoriale":
    analyse_territoriale(df, pathologie)

elif page == "Analyse temporelle":
    analyse_temporelle(df, pathologie)

elif page == "Anomalies":
    anomalies(df, pathologie)