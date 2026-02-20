import streamlit as st
from core.stats_pandas import charger_effectifs

st.set_page_config(page_title="Dashboard Analyse des pathologies",
                   layout="wide")


@st.cache_data
def load_data():
    return charger_effectifs()

df = load_data()

st.sidebar.title("Filtres globaux")

sexe = st.sidebar.selectbox("Sexe", [None] + sorted(df["libelle_sexe"].unique()))
age = st.sidebar.selectbox("Age", [None] + sorted(df["libelle_classe_age"].unique()))
departement = st.sidebar.selectbox("Département", [None] + sorted(df["departement"].unique()))
annee = st.sidebar.selectbox("Année", [None] + sorted(df["annee"].unique()))

st.session_state["df"] = df
st.session_state["filtre"]= {
    "sexe": sexe,
    "age" : age,
    "departement": departement,
    "annee": annee
}

st.title("Analyse nationale des pathologies - effectifs de patients pris en charge par l'ensemble des régimes d'assurance maladie (de 2015 à 2023)")
st.markdown("Utiliser le menu pour naviguer.")