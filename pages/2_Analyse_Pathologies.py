import streamlit as st
import plotly.express as px
from core.stats_pandas import (
    stats_patho,
    stats_par_sexe,
    stats_par_tranche_age,
    stats_par_annee,
    tendance_generale,
    pente_tendance
)

df = st.session_state["df"]

st.title("Analyse détaillée d'une pathologie")

pathologie = st.selectbox(
    "Choisir une pathologie",
    sorted(df["pathologie"].unique())
)

stats = stats_patho(df, pathologie)

col1, col2, col3 = st.columns(3)

col1.metric("Prévalence globale (%)", stats["prevalence_globale"])
col2.metric("Moyenne (%)", stats["prevalence_moyenne"])
col3.metric("Écart-type", stats["ecart_type"])

st.subheader("Tendance")

tendance = tendance_generale(df, pathologie)
pente = pente_tendance(df, pathologie)

st.write("Tendance générale :", tendance)
st.write("Pente annuelle moyenne :", pente)

st.subheader("Évolution annuelle")

df_annee = stats_par_annee(df, pathologie)

if df_annee is not None and not df_annee.empty:
    fig = px.line(
        df_annee.reset_index(),
        x="annee",
        y="prevalence_globale",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Analyse par sexe")
df_sexe = stats_par_sexe(df, pathologie)
if not df_sexe.empty:
    st.dataframe(df_sexe)

st.subheader("Analyse par tranche d'âge")
df_age = stats_par_tranche_age(df, pathologie)
if not df_age.empty:
    st.dataframe(df_age)