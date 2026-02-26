import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from core.stats_pandas import (
    stats_par_annee, variation_annuelle, tendance_generale, pente_tendance,
    moyenne_nationale_annee, z_score_prevalence_annee, stats_par_departement_annee
)

def analyse_temporelle(df: pd.DataFrame, pathologie: str) -> dict:

    st.title("Analyse temporelle d'une pathologie/traitement")
    st.caption(f"Analyse temporelle de la pathologie/traitement suivant : {pathologie}")


    # Filtre période

    annee_disponibles = sorted(df["annee"].unique())
    annee_min, annee_max = min(annee_disponibles), max(annee_disponibles)

    st.markdown("""
                ### Sélection de la période d'étude
                
                Le filtre ci-dessus permet d'analyser l'évolution de la pathologie sur une période spécifique.
                """)
    
    periode = st.slider(
        "Choisir une période",
        min_value=annee_min,
        max_value=annee_max,
        value=(annee_min, annee_max)
    )

    df_periode = df[(df["annee"] >= periode[0]) & (df["annee"] <= periode[1])]


    # Indicateurs synthètiques

    stats_annee = stats_par_annee(df_periode, pathologie)

    if stats_annee is None or stats_annee.empty:
        st.warning("Aucune donnée disponible sur cette périodes.")
        return
    

    annee_debut = stats_annee.index[0]
    annee_fin = stats_annee.index[-1]

    prev_debut = stats_annee.iloc[0]["prevalence_gloable"]
    prev_fin = stats_annee.iloc[-1]['prevalence_globale']

    tendance = tendance_generale(df_periode, pathologie)
    pente= pente_tendance(df_periode, pathologie)

    st.markdown("""
        ### Indicateurs clés
                
            Ces indicateurs synthétisent la dynamique globale entre la première année sélectionnée et 
                la deuxième année sélectionnée.
                """)
    

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Annee du début", annee_debut)
    col2.metric("Annee de fin", annee_fin)
    col3.metric("Prévalence du début (%)", prev_debut)
    col4.metric("Prevalence de fin (%)", prev_fin)