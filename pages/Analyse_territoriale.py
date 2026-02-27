import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from core.stats_pandas import (
    stats_par_departement, classement_departements, moyenne_nationale, ecart_a_la_moyenne,
    top_departements, bottom_departements, z_score_prevalence, valeurs_aberrantes
)
from utils.conversion import Conversion_donnees
import plotly.express as px
import json



def analyse_territoriale(df: pd.DataFrame, pathologie: str):

    st.title("Analyse territoriale d'une pathologie/traitement")
    st.caption(f"Analyse géographique de la pathologie/traitement suivant : {pathologie}")
    stats_dept = stats_par_departement(df, pathologie)

    # Indicateurs nationaux
    st.subheader("Résumé national")

    moy_nationale = moyenne_nationale(df, pathologie)
    max_prev = stats_dept["prevalence_globale"].max()
    min_prev = stats_dept["prevalence_globale"].min()
    ecart_type = stats_dept["prevalence_globale"].std()

    col1, col2, col3, col4 = st.columns(4)

    if moy_nationale is not None:
        col1.metric("Prévalence nationale (%)", moy_nationale)

    if ecart_type is not None:
        col2.metric("Ecart-type de la prévalence (%)", round(ecart_type, 3))

    if max_prev is not None:
        col3.metric("Prévalence max (%)", round(max_prev, 3))

    if min_prev is not None:
        col4.metric("Prévalence min (%)", round(min_prev, 3))

    st.divider()

    # Classement départements

    st.subheader("Classement des départements")

    classement = classement_departements(df, pathologie)

    st.dataframe(classement)

    st.markdown(
    """
    Cette section présente le **classement des départements** selon la prévalence de la pathologie sélectionnée.  
    - Les départements sont triés du moins touché au plus touché.  
    - Le tableau affiche  :
        - `dept` : le code du département  
        - `departement_nom` : le nom du département  
        - `prevalence_globale` : prévalence globale (%) dans le département  
    - Cela permet d'identifier rapidement les zones géographiques où la pathologie est la plus fréquente et celles où elle l'est moins.
    """)

    st.divider()


    #Carte Prévalence par département

    st.subheader("Carte de prévalence par département (hors DOM-TOM)")


    stats_carte = stats_dept.reset_index()

    @st.cache_data
    def charger_geojson():
        with open("data/departements.geojson", "r", encoding="utf-8") as f:
            return json.load(f)
        
    geojson = charger_geojson()

    fig2 = px.choropleth(
        stats_carte,
        geojson=geojson,
        locations="dept",
        featureidkey="properties.code",
        color="prevalence_globale",
        hover_name="departement_nom",
        color_continuous_scale="Reds"
    )

    fig2.update_geos(fitbounds="locations", visible=False)
    fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig2, use_container_width=True)   

    st.markdown(
    """
    Cette carte représente la **prévalence de la pathologie** par département.  

    - Chaque département est coloré selon sa prévalence globale (%), du plus clair (faible prévalence) au plus foncé (prévalence élevée).  
    - Le survol d’un département affiche son **nom** et sa **prévalence globale exacte**.  
    - Cette visualisation permet de **repérer rapidement les zones géographiques** où la pathologie est la plus fréquente et celles où elle est moins répandue.  
    - Les données sont basées sur le calcul de `stats_par_departement`, qui agrège les cas par département.  
    """
    ) 

    st.divider()

    # Top / Bottom 10

    st.subheader("Top / Bottom 10")

    col5, col6 = st.columns(2)

    with col5:
        st.markdown("### Top 10")
        top10 = top_departements(df, pathologie)
        st.dataframe(top10)

    with col6:
        st.markdown("### Bottom 10")
        bottom10 = bottom_departements(df, pathologie)
        st.dataframe(bottom10)

    st.markdown(
    """
    Cette section présente le **Top 10 et Bottom 10 des départements** pour la pathologie sélectionnée.  

    - **Top 10** : les départements les plus touchés par la pathologie, classés par prévalence décroissante.  
    - **Bottom 10** : les départements les moins touchés, classés par prévalence croissante.  
    - Les tableaux permettent de **comparer rapidement les zones les plus et moins affectées**, en donnant une vision de la répartition territoriale.  
    - Les colonnes affichées incluent :
        - `dept` : le code du département  
        - `departement_nom` : le nom du département  
        - `prevalence_globale` : prévalence globale (%) dans le département  
    """)
    
    st.divider()


    # Ecart à la moyenne nationale

    df_ecart = ecart_a_la_moyenne(df, pathologie)

    fig3 = px.bar(
    df_ecart,
    x="ecart_a_la_moyenne",
    y="departement_nom",
    orientation="h",
    title="Ecart à la moyenne nationale",
    height=1500,
    labels={"ecart_a_la_moyenne": "Écart (%)", "departement_nom": "Département"})

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
    """
    Ce graphique montre l'**écart de prévalence de chaque département par rapport à la moyenne nationale** pour la pathologie sélectionnée.  

    - L'axe horizontal (`Écart (%)`) représente la différence entre la prévalence départementale et la prévalence nationale.  
    - L'axe vertical affiche les départements (`Département`).  
    - Les barres à droite de zéro indiquent des départements où la prévalence est supérieure à la moyenne nationale,  
    tandis que les barres à gauche indiquent une prévalence inférieure à la moyenne.  
    - Cette visualisation permet d'identifier rapidement les départements **au-dessus ou en dessous de la moyenne nationale**.
    """)

    st.divider()


    # Valeur aberrantes (z-score)

    st.subheader("Départements atypiques (z-score) >= 2")

    df_aberrantes = valeurs_aberrantes(df, pathologie)

    if df_aberrantes.empty:
        st.info("Aucune valeur aberrante détectée")

    else:
        st.dataframe(df_aberrantes)

    st.markdown(
    """
    Cette section met en évidence les **départements présentant des valeurs atypiques** pour la pathologie sélectionnée,  
    en utilisant le **z-score** comme indicateur statistique.  

    - Un z-score supérieur ou égal à 2 indique que la prévalence du département est **significativement différente de la moyenne nationale**.  
    - Le tableau affiche les départements concernés ainsi que leurs valeurs correspondantes, permettant d’identifier rapidement les anomalies géographiques.  
    - Si aucun département n’est détecté, cela signifie que toutes les prévalences sont proches de la moyenne nationale.""")