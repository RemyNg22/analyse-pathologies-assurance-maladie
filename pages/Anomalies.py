import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from core.stats_pandas import (z_score_prevalence, valeurs_aberrantes, z_score_prevalence_annee, annees_anormales)
import plotly.express as px

def anomalies(df: pd.DataFrame, pathologie: str):

    st.title("Analyse des anomalies statistiques d'une pathologie/traitement")
    st.caption(f"Analyse des anomalies de la pathologie/traitement suivant : {pathologie}")

    st.divider()

    # Anomalies départementales (cumul sur la période étudiée)

    st.subheader("Départements atypiques (z-score cumulé sur les 9 ans étudiés, seuil = 2)")
    df_z = z_score_prevalence(df, pathologie)
    if df_z.empty:
        st.info("Aucune donnée disponible.")
        return

    df_aberrants = valeurs_aberrantes(df, pathologie)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Départements analysés", len(df_z))

    with col2:
        st.metric("Anomalies détectées (z_score ≥ 2)", len(df_aberrants))

    with col3:
        st.metric("Z-score maximal", round(df_z["z_score"].abs().max(), 3))


    df_z_sorted = df_z.sort_values("z_score")
    fig = px.bar(
        df_z_sorted,
        x="z_score",
        y="departement_nom",
        orientation="h",
        title="Distribution des écarts standardisés départementaux",)

    fig.add_vline(x=2, line_dash="dash",
                        line_color="red",
                        line_width=2)
    fig.add_vline(x=-2, line_dash="dash",
                        line_color="red",
                        line_width=2)

    fig.update_layout(
        yaxis_title="Département",
        xaxis_title="Z-score",
        height=2000)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
    **Interprétation**

    - Le z-score mesure l'écart d'un département à la moyenne nationale.
    - Les lignes pointillées correspondent au seuil statistique fixé à +2 ou -2.
    - Un z-score ≥ 2 indique un écart significatif.
    - Cette mesure est calculée sur le cumul de toutes les années disponibles.

    Un z-score positif traduit une prévalence supérieure à la moyenne nationale.  
    Un z-score négatif traduit une prévalence inférieure.
    """)

    if not df_aberrants.empty:
        st.markdown("#### Départements présentant une anomalie statistique")
        st.dataframe(df_aberrants)
    else:
        st.success("Aucun département ne dépasse le seuil de ±2.")

    st.divider()

    # Années normales (dispersion territoriale)


    st.subheader("Années présentant une dispersion atypique (seuil = 2)")

    df_annees = annees_anormales(df, pathologie)

    if df_annees.empty:
        st.success("Aucune année ne présente une dispersion moyenne ≥ 2.")
    else:
        fig2, ax2 = plt.subplots()
        ax2.bar(df_annees["annee"], df_annees["moyenne_abs_z"])
        ax2.set_xlabel("Année")
        ax2.set_ylabel("Moyenne absolue des z-scores")
        ax2.set_title("Années à forte hétérogénéité territoriale")
        st.pyplot(fig2)

        st.markdown(
            """
    **Interprétation**

    - Pour chaque année, on calcule la moyenne absolue des z-scores départementaux.
    - Si cette moyenne est >= 2, l'année est considérée comme atypique.
    - Cela signifie qu'en moyenne, les départements s'écartent fortement de la moyenne nationale.

    Une telle situation peut traduire :
    - une rupture sanitaire,
    - un changement de méthodologie,
    - une dynamique territoriale exceptionnelle.""")

        st.dataframe(df_annees)

    st.divider()

    # Heatmap dynamique (anomalies par année)

    st.subheader("Cartographie des anomalies département et année")

    df_z_annuel = z_score_prevalence_annee(df, pathologie)

    if df_z_annuel.empty:
        st.info("Données insuffisantes pour analyse annuelle.")
        return

    pivot = df_z_annuel.pivot(
        index="departement_nom",
        columns="annee",
        values="z_score")

    fig3 = px.imshow(pivot,
        aspect="auto",
        color_continuous_scale="RdBu",
        origin="lower",
        title="Heatmap des z-scores par année")
    
    fig3.update_layout(height=1000)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
            """
    **Lecture de la heatmap**

    - Chaque cellule correspond au z-score d'un département pour une année donnée.
    - Une valeur ≥ 2 ou ≤ -2 signale une anomalie relative cette année-là.
    - Une intensité forte répétée sur plusieurs années suggère une anomalie structurelle.
    - Une cellule isolée traduit plutôt un événement ponctuel.

    Cette vue permet d'identifier :
    - des départements durablement atypiques,
    - des ruptures temporelles,
    - des phénomènes localisés.""")

    #Volatilité des département

    st.subheader("Volatilité des départements dans le temps")

    df_vol = (df_z_annuel.groupby("departement_nom")["z_score"]
        .std().reset_index().rename(columns={"z_score": "volatilite"})
        .sort_values("volatilite", ascending=False))
    
    df_vol_top = df_vol.head(20)
    fig4 = px.bar(df_vol_top.sort_values("volatilite"),
        x="volatilite",
        y="departement_nom",
        orientation="h",
        title="Top 20 des départements les plus volatils")

    fig4.update_layout(yaxis_title="Département",
        xaxis_title="Écart-type des z-scores",
        height=800)

    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(
    """
    **Interprétation**

    - Une volatilité faible indique un département structurellement stable.
    - Une volatilité élevée traduit des variations importantes d’une année à l’autre.
    - Une forte volatilité sans z-score extrême peut indiquer des oscillations régulières.

    Ce score permet d’identifier les territoires instables même sans anomalie ponctuelle majeure.
    """
    )
    st.dataframe(df_vol.head(10))

    #Instabilité territoriale

    st.subheader("Indice global d’instabilité territoriale")

    instabilite = df_z["z_score"].abs().mean()

    st.metric("Moyenne absolue des z-scores", round(instabilite, 3))

    st.markdown(
    """
    **Interprétation**

    - < 0.5 -> distribution homogène
    - 0.5 à 1 -> dispersion modérée
    - 1 à 2 -> forte hétérogénéité
    - supérieur ou égal 2 -> déséquilibre structurel important

    Cet indicateur synthétise le niveau global d'écart entre départements.
    """
    )