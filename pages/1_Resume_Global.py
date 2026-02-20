import streamlit as st
from core.stats_pandas import (
    resume_global_avance,
    nombre_de_lignes,
    pathologies_distinctes,
    departements_distincts,
    annees_distinctes
)

df = st.session_state["df"]
f = st.session_state["filtres"]

st.title("Résumé global")

resume = resume_global_avance(
    df,
    sexe=f["sexe"],
    age=f["age"],
    departement=f["departement"],
    annee=f["annee"]
)

if resume is None:
    st.warning("Aucune donnée disponible.")
else:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Cas totaux", f"{resume['total_ntop']:,}")
    col2.metric("Population totale", f"{resume['total_npop']:,}")
    col3.metric("Prévalence globale (%)", resume["prevalence_globale"])
    col4.metric("Nombre de pathologies", pathologies_distinctes(df))

st.subheader("Informations structurelles")

colA, colB, colC = st.columns(3)
colA.metric("Nombre de lignes", nombre_de_lignes(df))
colB.metric("Départements", departements_distincts(df))
colC.metric("Années", annees_distinctes(df))