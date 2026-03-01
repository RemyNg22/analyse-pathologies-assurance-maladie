import streamlit as st
from core.stats_pandas import charger_effectifs
from modules.Resume_Global import resume_global, page_resume_global
from modules.Analyse_Pathologies import analyse_pathologie
from modules.Analyse_territoriale import analyse_territoriale
from modules.Analyse_temporelle import analyse_temporelle
from modules.Anomalies import anomalies

"""
Application principale du dashboard d'analyse des pathologies/traitements pris en charge.

### Rôle de l’application

- Charger les données  
- Appeler les fonctions d'analyse (`stats_pandas.py`)  
- Visualiser les statistiques par pathologies/traitements  s

**Navigation :**  
La navigation s’effectue exclusivement via le **menu déroulant dans la barre latérale**.
"""

# Chargement des données
@st.cache_data
def load_data():
    return charger_effectifs()

df = load_data()

st.set_page_config(page_title="Dashboard Pathologies/Traitements", layout="wide")

st.divider()

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
    pathologie = st.sidebar.selectbox("Choisir une pathologie/traitements", sorted(df["pathologie"].unique()))

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

