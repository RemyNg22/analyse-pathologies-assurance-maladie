import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from core.stats_pandas import (
    stats_par_annee, variation_annuelle, tendance_generale, pente_tendance, z_score_prevalence_annee, stats_par_departement_annee
)

def analyse_temporelle(df: pd.DataFrame, pathologie: str) -> dict:

    st.title("Analyse temporelle d'une pathologie/traitement")
    st.caption(f"Analyse temporelle de la pathologie/traitement suivant : {pathologie}")


    # Filtre période

    annee_disponibles = sorted(df["annee"].unique())
    annee_min, annee_max = min(annee_disponibles), max(annee_disponibles)

    st.markdown("""
                ### Sélection de la période d'étude
                
                Le filtre ci-dessous permet d'analyser l'évolution de la pathologie sur une période spécifique.
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

    prev_debut = stats_annee.iloc[0]["prevalence_globale"]
    prev_fin = stats_annee.iloc[-1]['prevalence_globale']

    tendance = tendance_generale(df_periode, pathologie)
    pente= pente_tendance(df_periode, pathologie)

    st.subheader("Indicateurs clés")
    
    col1, col2, col3, col4 = st.columns(4)

    

    col1.metric("Annee du début", annee_debut)
    col2.metric("Annee de fin", annee_fin)
    col3.metric("Prévalence de la premère année (%)", prev_debut)
    col4.metric("Prevalence de la dernière année (%)", prev_fin)


    st.markdown("""Ces indicateurs synthétisent la dynamique globale entre la première année sélectionnée et 
                la deuxième année sélectionnée pour une pathologie/traitement.""")
    
    st.write("")
    st.write("")

    col5, col6 = st.columns(2)
    col5.metric("Tendance générale", tendance)
    col6.metric("Pente annuelle moyenne", pente)

    st.markdown(f"""Nous voyons donc qu'entre l'année {annee_debut} et l'année {annee_fin}, la prévalence globale est en {tendance} 
    avec une pente annuelle moyenne de {pente}%.""")


    st.divider()

    
    # Courbe d'évolution et moyenne nationale

    st.subheader("Evolution annuelle de la prévalence")


    fig1, ax1 = plt.subplots()

    ax1.plot(
        stats_annee.index,
        stats_annee["prevalence_globale"],
        marker="o",
        label="Prévalence pathologie"
    )


    ax1.set_xlabel("Année")
    ax1.set_ylabel("Prévalence (%)")
    ax1.set_title(f"Evolution annuelle ({pathologie})")
    ax1.legend()
    st.pyplot(fig1)

    st.markdown("""La courbe montre l'évolution annuelle de la prévalence nationale.""")
    

    st.divider()

    # Variations absolues

    st.subheader("Variations annuelles de la prévalence")

    variations = variation_annuelle(df_periode, pathologie)

    if variations:
        df_variation = pd.DataFrame(variations).T
        df_variation.index.name = "Année"

        fig2, ax2 = plt.subplots()

        ax2.bar(
            df_variation.index,
            df_variation["difference absolue"]
        )
        ax2.axhline(0)
        ax2.set_xlabel("Année")
        ax2.set_ylabel("Variation absolue (%)")
        ax2.set_title(f"Variation annuelle ({pathologie})")
        st.pyplot(fig2)

        st.markdown("""
        Chaque barre représente l’évolution entre une année et l’année précédente.

        - Une barre au-dessus de 0 signifie que la prévalence a augmenté.
        - Une barre en dessous de 0 signifie qu’elle a diminué.
        - Plus la barre est haute (ou basse), plus le changement est important.

        Ce graphique permet d’identifier :

        - Les années où la progression a été forte
        - Les années de ralentissement ou de baisse
        - Les éventuelles ruptures dans la dynamique globale
        """)
        st.write("")
        st.write("")
        
        st.dataframe(df_variation)

        st.markdown("""
        Le tableau détaille les variations d’une année à l’autre :

        - Différence absolue : variation en points de pourcentage.
        - Valeur relative : variation en % par rapport à l’année précédente.

        Il complète le graphique en apportant le niveau exact des changements.
        """)

    else:
        st.info("Pas assez d'années pour calculer les variations. Veuillez sélectionner une tranche plus élévée.")

    st.divider()


    # Intensité écarts territoriaux

    st.subheader("Intensité des écarts territoriaux")

    df_z_score = z_score_prevalence_annee(df_periode, pathologie)

    if not df_z_score.empty:
        df_moy_abs = (
            df_z_score.groupby("annee")["z_score"].apply(lambda x: x.abs().mean()).reset_index(name="moyenne_abs_z"))

        fig3, ax3 = plt.subplots(figsize=(8,5))
        ax3.plot(df_moy_abs["annee"], df_moy_abs["moyenne_abs_z"], marker="o", label="Dispersion moyenne")
        
        seuil = 2
        ax3.axhline(seuil, color='red', linestyle='--', label=f'Seuil de forte dispersion ({seuil})')
        
        ax3.set_xlabel("Année")
        ax3.set_ylabel("Moyenne absolue des z-scores")
        ax3.set_title(f"Dispersion territoriale annuelle ({pathologie})")
        ax3.legend()
        st.pyplot(fig3)

        st.markdown(f"""
        Chaque point représente la **dispersion moyenne des départements** pour cette année.  
        - Plus la valeur est proche de 0, plus les départements sont proches de la moyenne nationale.  
        - Plus la valeur est élevée, plus les écarts territoriaux sont importants.  
        - La ligne rouge représente un **seuil de 2**, au-dessus duquel la dispersion est considérée comme forte.  
        
        Ce seuil se base sur la règle statistique des z-scores: dans une distribution normale, la majorité des valeurs se situent entre -2 et +2.  
        Si cela dépasse ce seuil, cela signifie que plusieurs départements s’écartent beaucoup de la moyenne nationale.
        """)

    else:
        st.info("Impossible de calculer les z-scores pour cette pathologie et période.")


    st.divider()


    # Distribution départementale annuelle (boxplot)

    st.subheader("Distribution départementale des prévalences")

    df_box = stats_par_departement_annee(df_periode, pathologie)

    if not df_box.empty:

        fig4, ax4 = plt.subplots(figsize=(10, 6))

        sns.boxplot(
            data=df_box,
            x="annee",
            y="prevalence_globale",
            ax=ax4
        )

        ax4.set_xlabel("Année")
        ax4.set_ylabel("Prévalence départementale (%)")
        ax4.set_title(f"Distribution annuelle des prévalences départementales ({pathologie})")

        st.pyplot(fig4)

        st.markdown("""
        Chaque boîte représente la distribution des 101 départements pour une année donnée :

        - La ligne centrale correspond à la médiane
        - La boîte représente les quartiles (Q1–Q3)
        - Les points isolés sont des départements atypiques

        Ce graphique permet d’analyser :
        - L’évolution de la dispersion
        - Le déplacement global du niveau médian
        - L’apparition éventuelle d’outliers structurels
        """)

    else:
        st.info("Pas de données disponibles.")