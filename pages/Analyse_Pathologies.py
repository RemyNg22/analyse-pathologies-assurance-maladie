# 2_Analyse_Pathologies.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from core.stats_pandas import (stats_patho, stats_par_sexe, stats_par_tranche_age, age_central_pathologie,
                               ratio_cas_hf, difference_prevalence_sexe, prevalence_globale)

def analyse_pathologie(df: pd.DataFrame, pathologie: str):

    st.title(f"Analyse d'une pathologie : {pathologie}")
    st.caption("Analyse démographique de la pathologie sélectionnée.")

    df_patho = df[df["pathologie"] == pathologie]

    # Indicateurs globaux

    stats_globales = stats_patho(df, pathologie)

    st.subheader("Indicateurs globaux")

    col1, col2, col3 = st.columns(3)

    col1.metric("Cas totaux", f"{int(stats_globales['Ntop_totale']):,}")
    col2.metric("Population totale", f"{int(stats_globales['Npop_totale']):,}")
    col3.metric("Prévalence globale (%)", f"{prevalence_globale(df_patho):.2f}")

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

    fig1, ax1 = plt.subplots()
    ax1.bar(stats_sexe.index, stats_sexe["Ntop_totale"])
    ax1.set_xlabel("Sexe")
    ax1.set_ylabel("Nombre de cas")
    ax1.set_title("Nombre de cas par sexe")

    st.pyplot(fig1)


    fig2, ax2 = plt.subplots()
    ax2.bar(stats_sexe.index, stats_sexe["prevalence_globale"])
    ax2.set_xlabel("Sexe")
    ax2.set_ylabel("Prévalence (%)")
    ax2.set_title("Prévalence globale par sexe")

    st.pyplot(fig2)

    st.subheader("Dispersion des prévalences : hommes")

    col8, col9, col10, col11 = st.columns(4)
    if "hommes" in stats_sexe.index:
        col8.metric("Moyenne", stats_globales["prevalence_moyenne"])
        col9.metric("Médiane", stats_globales["prevalence_mediane"])
        col10.metric("Min", stats_globales["prevalence_min"])
        col11.metric("Max", stats_globales["prevalence_max"])

        st.caption(f"Ecart-type : {stats_globales['ecart_type']}")

    st.subheader("Dispersion des prévalences : femmes")

    col8, col9, col10, col11 = st.columns(4)
    if "femmes" in stats_sexe.index:
        col8.metric("Moyenne", stats_globales["prevalence_moyenne"])
        col9.metric("Médiane", stats_globales["prevalence_mediane"])
        col10.metric("Min", stats_globales["prevalence_min"])
        col11.metric("Max", stats_globales["prevalence_max"])

        st.caption(f"Ecart-type : {stats_globales['ecart_type']}")


    pivot = df[df["pathologie"] == pathologie].groupby(["libelle_classe_age", "libelle_sexe"])["Ntop"].sum().unstack()

    pivot.plot(kind="barh")
    st.pyplot(plt.gcf())

    st.divider()

    # =============================
    # 3️⃣ Répartition par âge
    # =============================

    st.subheader("Structure par tranche d'âge")

    stats_age = stats_par_tranche_age(df, pathologie)

    fig2, ax2 = plt.subplots()
    ax2.barh(stats_age["tranche_age"], stats_age["Ntop_totale"])
    ax2.set_xlabel("Nombre de cas")
    ax2.set_title("Distribution des cas par tranche d'âge")

    st.pyplot(fig2)

    total_age = stats_age["Ntop_totale"].sum()
    stats_age["%"] = (stats_age["Ntop_totale"] / total_age * 100).round(2)

    st.dataframe(stats_age)

    st.divider()

    # =============================
    # 4️⃣ Âge central
    # =============================

    age_central = age_central_pathologie(df, pathologie)

    st.subheader("Tranche d'âge centrale")
    st.info(f"La tranche d'âge la plus représentée est : {age_central}")

    st.markdown(
        """
        Cette tranche concentre le volume de cas le plus important.
        Cela permet d'identifier la population prioritaire concernée.
        """
    )