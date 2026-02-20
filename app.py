import streamlit as st
from core.stats_pandas import charger_effectifs
from pages.Resume_Global import resume_global
from pages.Analyse_Pathologies import analyse_pathologie
from pages.Analyse_territoriale import analyse_territoriale
from pages.Analyse_temporelle import analyse_temporelle
from pages.Anomalies import anomalies

st.write("App démarre correctement !")

st.set_page_config(page_title="Dashboard Pathologies", layout="wide")

# Chargement des données
@st.cache_data
def load_data():
    return charger_effectifs()

df = load_data()

# Sidebar : sélection de la page
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
if page != "Résumé global":
    pathologie = st.sidebar.selectbox(
        "Choisir une pathologie",
        sorted(df["pathologie"].unique())
    )


# Navigation
if page == "Résumé global":
    st.header("Résumé global")
    global_stats = resume_global(df)
    st.write(global_stats)

elif page == "Analyse par pathologie":
    st.header("Analyse par pathologie")
    patho_stats = analyse_pathologie(df, pathologie)
    st.write("Statistiques globales")
    st.write(patho_stats["stats_globales"])
    st.write("Stats par sexe")
    st.dataframe(patho_stats["stats_par_sexe"])
    st.write("Stats par tranche d'âge")
    st.dataframe(patho_stats["stats_par_age"])
    st.write("Tranche d'âge centrale")
    st.write(patho_stats["age_central"])

elif page == "Analyse territoriale":
    st.header("Analyse territoriale")
    territoire_stats = analyse_territoriale(df, pathologie)
    st.write("Stats par département")
    st.dataframe(territoire_stats["stats_departement"])
    st.write("Top 10 départements")
    st.dataframe(territoire_stats["top10_departements"])
    st.write("Bottom 10 départements")
    st.dataframe(territoire_stats["bottom10_departements"])

elif page == "Analyse temporelle":
    st.header("Analyse temporelle")
    temp_stats = analyse_temporelle(df, pathologie)
    st.write("Stats par année")
    st.dataframe(temp_stats["stats_par_annee"])
    st.write("Variation annuelle")
    st.write(temp_stats["variation_annuelle"])
    st.write("Tendance générale")
    st.write(temp_stats["tendance_generale"])
    st.write("Pente annuelle")
    st.write(temp_stats["pente_tendance"])

elif page == "Anomalies":
    st.header("Anomalies")
    anomalies_stats = anomalies(df, pathologie)
    st.write("Départements aberrants")
    st.dataframe(anomalies_stats["departements_aberrants"])
    st.write("Années aberrantes")
    st.dataframe(anomalies_stats["annees_aberrantes"])