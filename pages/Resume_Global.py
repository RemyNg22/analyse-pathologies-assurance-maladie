import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from core.stats_pandas import (
    nombre_de_lignes, pathologies_distinctes, departements_distincts, annees_distinctes,
    nombre_de_cas, population_reference, prevalence_globale, prevalence_moyenne
)

def resume_global(df: pd.DataFrame) -> dict:
    """
    Résumé global des données.
    """
    return {
        "Nombre de lignes": nombre_de_lignes(df),
        "Nombre de pathologies distinctes": pathologies_distinctes(df),
        "Nombre de départements distincts": departements_distincts(df),
        "Nombre d'années distinctes": annees_distinctes(df),
        "Nombre total de cas": nombre_de_cas(df),
        "Population totale": population_reference(df),
        "Prévalence globale (%)": prevalence_globale(df),
        "Prévalence moyenne (%)": prevalence_moyenne(df)
    }

def page_resume_global(df: pd.DataFrame):

    st.title("Résumé global")
    st.caption("Synthèse du jeu de données et des indicateurs épidémiologiques.")

    stats = resume_global(df)

    st.subheader("Structure du jeu de données")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Lignes", f"{stats['Nombre de lignes']:,}")
    col2.metric("Pathologies", stats["Nombre de pathologies distinctes"])
    col3.metric("Départements", stats["Nombre de départements distincts"])
    col4.metric("Années couvertes", stats["Nombre d'années distinctes"])

    st.markdown(
        """
        Ces indicateurs décrivent les données suivantes :
        - le volume total de lignes observées,
        - la diversité des pathologies étudiées,
        - la couverture territoriale,
        - et la profondeur temporelle.
        """
    )

    st.markdown(
    """
    Les lignes correspondent au jeu de données filtré :
    les agrégats nationaux ("Toute la France"), les modalités globales ("tous sexes") 
    et les lignes avec des données manquantes ont été exclus afin d’éviter les doubles 
    comptages ou données qui fausseraient les statistiques.
    """)

    st.divider()


    st.subheader("Indicateurs généraux")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Cas totaux", f"{stats['Nombre total de cas']:,}")
    col2.metric("Population totale", f"{stats['Population totale']:,}")
    col3.metric("Prévalence globale", f"{stats['Prévalence globale (%)']:.2f} %")
    col4.metric("Prévalence moyenne", f"{stats['Prévalence moyenne (%)']:.2f} %")

    st.markdown(
        """
        - **Prévalence globale** : proportion totale de cas rapportée à la population de référence
        - **Prévalence moyenne** : moyenne des prévalences calculées sur les sous-groupes
        """
    )

    st.markdown(
        """
        Les cas totaux correspondent à l’ensemble des cas recensés sur la période
        de 9 ans. Un même patient peut apparaître plusieurs fois s’il est concerné
        par plusieurs pathologies ou plusieurs prises en charge.
        """
    )

    st.divider()


    st.subheader("Évolution globale des cas")

    cas_par_annee = df.groupby("annee")["Ntop"].sum().sort_index()

    fig, ax = plt.subplots()
    ax.plot(cas_par_annee.index, cas_par_annee.values)
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre total de cas")
    ax.set_title("Nombre total de cas par année")
    ax.ticklabel_format(style='plain', axis='y')
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))    
    ax.grid(True)

    st.pyplot(fig)


    st.markdown(
        """
        Ce graphique permet d'identifier :
        - une tendance (hausse ou baisse),
        - des ruptures éventuelles,
        - des années atypiques.
        
        Une augmentation peut refléter une évolution réelle de la pathologie,
        mais aussi un changement de méthodologie ou de dépistage.
        """
    )


    st.divider()


    st.subheader("Top 20 des pathologies et traitements pris en charge (cas cumulés)")

    top_pathologies = (df.groupby("pathologie")["Ntop"].sum().sort_values(ascending=False))
    top_pathologies = top_pathologies.iloc[2:22]
    top_pathologies = top_pathologies[::-1]
    fig2, ax2 = plt.subplots()
    ax2.barh(top_pathologies.index, top_pathologies.values)
    ax2.set_xlabel("Nombre total de cas")
    ax2.set_title("Pathologies/traitements les plus représentées")
    st.pyplot(fig2)

    st.markdown(
        """
        Cette visualisation met en évidence les pathologies/traitements concentrant
        le plus grand volume de cas sur la période étudiée.

        Cette visualisation met en évidence les pathologies concentrant
        le plus grand volume de cas sur la période étudiée.

        Une forte concentration sur quelques pathologies peut orienter
        les priorités d'analyse pour les pages suivantes.
        
        **Note :** les deux première lignes (non affichées ici) correspondent à des hospitalisations ou prises en charge
        sans pathologie spécifique identifiée (traitements, maternité, antalgique/anti-inflammatoire). 
        Ces cas ne reflètent pas de pathologie particulière et ont été exclus du graphique.
        Les deux premières lignes masquées sont les suivantes :

        - **Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire** : 1.293.429.190 cas,
        - **Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité)** : 347.187.090 cas
        """
    )

    st.divider()


    st.subheader("Répartition globale des cas par département")

    cas_par_departement = (df.groupby("departement")["Ntop"].sum().sort_values(ascending=False).head(10))

    fig3, ax3 = plt.subplots()
    ax3.bar(cas_par_departement.index.astype(str), cas_par_departement.values)
    ax3.set_xlabel("Département")
    ax3.set_ylabel("Nombre total de cas")
    ax3.set_title("Top 10 départements en volume de cas")
    ax3.tick_params(axis='x', rotation=45)
    ax3.ticklabel_format(style='plain', axis='y')
    ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))    

    st.pyplot(fig3)

    st.markdown(
        """
        Cette analyse brute en volume doit être interprétée avec prudence.
        Les départements avec le plus de pathologies et traitements pris en charge 
        au cours des 9 dernières années apparaissent en tête.
        
        L'analyse territoriale détaillée permettra d'examiner les prévalences
        afin d'ajuster pour l'effet population.
        """
    )