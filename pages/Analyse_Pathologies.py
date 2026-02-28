import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from core.stats_pandas import (stats_patho, stats_par_sexe, stats_par_tranche_age, age_central_pathologie,
                               ratio_cas_hf, difference_prevalence_sexe, prevalence_globale)
from utils.conversion import Conversion_donnees

def analyse_pathologie(df: pd.DataFrame, pathologie: str):

    st.title("Analyse d'une pathologie/traitement")
    st.caption(f"Analyse démographique du traitement ou de la pathologie suivant(e) : {pathologie}")

    df_patho = df[df["pathologie"] == pathologie]

    # Indicateurs globaux

    stats_globales = stats_patho(df, pathologie)

    st.subheader("Indicateurs globaux")

    col1, col2, col3 = st.columns(3)

    col1.metric("Cas totaux", f"{int(stats_globales['Ntop_totale']):,}")
    col2.metric("Population totale", f"{int(stats_globales['Npop_totale']):,}")
    col3.metric("Prévalence globale (%)", f"{prevalence_globale(df_patho):.2f}")

    st.markdown("""
    Cette section présente les indicateurs agrégés pour la pathologie sélectionnée.

    - **Cas totaux** : nombre total de patients pris en charge sur les 9 dernières années.
    - **Population totale** : population exposée au risque.
    - **Prévalence globale** : proportion de patients concernés dans la population totale.

    La prévalence permet d’évaluer le poids relatif de la pathologie indépendamment de la taille démographique.
    """)

    st.divider()


    # Répartition par sexe

    st.subheader("Structure par sexe")

    stats_sexe = stats_par_sexe(df, pathologie)
    ratio = ratio_cas_hf(df, pathologie)
    diff_prev = difference_prevalence_sexe(df, pathologie)

    col4, col5, col6, col7 = st.columns(4)

    if ratio:
        col4.metric("Ratio H/F (cas)", ratio)

    if diff_prev:
        col5.metric("Différence prévalence H - F (%)", diff_prev)

    if "hommes" in stats_sexe.index:
        col6.metric("Prévalence Hommes (%)", stats_sexe.loc["hommes", "prevalence_globale"])
    
    if "femmes" in stats_sexe.index:
        col7.metric("Prévalence Femmes (%)", stats_sexe.loc["femmes", "prevalence_globale"])

    st.markdown("### **Répartition des cas et de la prévalence par sexe**")
    st.markdown("Le graphique ci-dessous présente le nombre total de cas par sexe.")

    fig1, ax1 = plt.subplots()
    ax1.bar(stats_sexe.index, stats_sexe["Ntop_totale"])
    ax1.set_xlabel("Sexe")
    ax1.set_ylabel("Nombre de cas")
    ax1.set_title("Nombre de cas par sexe")
    ax1.ticklabel_format(style='plain', axis='y')
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))  
    st.pyplot(fig1)

    st.write("")
    st.write("")
    st.markdown("Le prochain présente :\n"
    "- la part entre hommes et femmes pour le traitement/pathologie concerné\n"
    "- la prévalence globale par sexe"
)

    labels = stats_sexe.index
    sizes = stats_sexe["prevalence_globale"]

    def autopct_remplissage(values):
        def inter_autopct(pct):
            total = sum(values)
            val = pct * total / 100
            return f"{pct:.1f}%\n({val:.2f}%)"
        return inter_autopct

    fig2, ax2 = plt.subplots()
    wedges, texts, autotexts = ax2.pie(
        sizes,
        labels=labels,
        autopct=autopct_remplissage(sizes),
        startangle=90,
        colors=["#1d45b3", "#f82408"],
        textprops=dict(color="w")
    )

    ax2.set_title("Prévalence globale par sexe")


    ax2.legend(wedges, labels, title="Sexe", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    st.pyplot(fig2)

    st.write("")
    st.write("")

    st.markdown("""
    L’analyse par sexe permet d’identifier d’éventuelles disparités épidémiologiques.

    Deux dimensions sont étudiées :
    - Le volume de cas.
    - Le taux de prévalence.

    Une différence de volume ne signifie pas nécessairement une différence de risque.
    La prévalence permet une comparaison à structure démographique équivalente.
    """)

    st.markdown("### **Dispersion des prévalences : hommes**")

    col8, col9, col10, col11 = st.columns(4)
    if "hommes" in stats_sexe.index:
        col8.metric("Moyenne", stats_globales["prevalence_moyenne"])
        col9.metric("Médiane", stats_globales["prevalence_mediane"])
        col10.metric("Min", stats_globales["prevalence_min"])
        col11.metric("Max", stats_globales["prevalence_max"])

        st.caption(f"Ecart-type : {stats_globales['ecart_type']}")

    st.markdown("### **Dispersion des prévalences : femmes**")

    col8, col9, col10, col11 = st.columns(4)
    if "femmes" in stats_sexe.index:
        col8.metric("Moyenne", stats_globales["prevalence_moyenne"])
        col9.metric("Médiane", stats_globales["prevalence_mediane"])
        col10.metric("Min", stats_globales["prevalence_min"])
        col11.metric("Max", stats_globales["prevalence_max"])

        st.caption(f"Ecart-type : {stats_globales['ecart_type']}")

    st.write("")
    st.write("")

    st.markdown("""
    Les indicateurs de dispersion permettent d’évaluer l’hétérogénéité territoriale.

    - **Moyenne** : niveau moyen de prévalence.
    - **Médiane** : valeur centrale.
    - **Min / Max** : amplitude observée.
    - **Écart-type** : niveau de variabilité.

    Une forte dispersion peut indiquer des inégalités territoriales marquées.
    """)

    st.markdown("### **Répartition des cas par tranche d'âge et par sexe**")
    df_filtered = df[(df["pathologie"] == pathologie) & (df["libelle_classe_age"] != "tous âges") & (df["libelle_sexe"] != "tous sexes")]

    df_filtered["libelle_classe_age"] = pd.Categorical(df_filtered["libelle_classe_age"], categories=Conversion_donnees.ORDRE_TRANCHES_AGE, ordered=True)

    pivot = df_filtered.groupby(["libelle_classe_age", "libelle_sexe"])["Ntop"].sum().unstack()

    pivot.plot(kind="barh")
    st.pyplot(plt.gcf())

    st.divider()


    # Répartition par âge

    st.subheader("Structure par tranche d'âge")

    stats_age = stats_par_tranche_age(df, pathologie)

    fig2, ax2 = plt.subplots()
    ax2.barh(stats_age.index, stats_age["Ntop_totale"])
    ax2.set_xlabel("Nombre de cas")
    ax2.set_title("Distribution des cas par tranche d'âge")
    ax2.ticklabel_format(style='plain', axis='x')
    ax2.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))  
    st.pyplot(fig2)
    st.markdown("""
    La structure par âge permet d’identifier les classes démographiques les plus concernées.
    Le calcul ici se fait, à la différence du tableau précédent, par le volument de cas tout sexe confondu.
    """)
    st.write("")
    st.write("")

    st.markdown("### **Tableau des prévalences et parts par tranche d'âge**")
    total_age = stats_age["Ntop_totale"].sum()
    stats_age["%"] = (stats_age["Ntop_totale"] / total_age * 100).round(3)
    stats_age = stats_age.reset_index().rename(columns={"libelle_classe_age" : "Tranche d'âge", "Ntop_totale": "Nombre total de cas", "Npop_totale": "Population totale", 
                                                        "prevalence_globale" : "Prevalence globale", "%": "Part (%)"})
    stats_age.index = stats_age.index + 1

    st.dataframe(stats_age)

    st.divider()

    # Âge central

    age_label, age_valeur = age_central_pathologie(df, pathologie)
    part_la_plus_elevee = stats_age.loc[stats_age["Part (%)"].idxmax(), "Tranche d'âge"]

    st.subheader("Tranche d'âge centrale")
    st.markdown(f"**La tranche d'âge la plus représentée est** : {age_label} ({age_valeur:.3f} %)")

    st.markdown(f"""
    ### Interprétation des résultats

    La tranche d’âge {age_label} présente la prévalence la plus élevée :  
    cela signifie que le **risque** d’être concerné par la pathologie 
    est maximal dans cette classe d’âge.""")

    if age_label != part_la_plus_elevee:
        st.markdown(f"""
        En revanche, la tranche {part_la_plus_elevee} représente la part (%) la plus importante 
        du total des cas observés.  

        Cette différence s’explique par la structure démographique :

        - La prévalence mesure un **taux (cas / population)**.
        - La part (%) mesure un **poids dans le volume total des cas**.
        - Une tranche d’âge plus nombreuse peut concentrer davantage de cas 
        même si son taux est légèrement inférieur.
        """)