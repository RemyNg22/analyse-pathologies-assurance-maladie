# 1_Resume_Global.py
import pandas as pd
from core.stats_pandas import (
    nombre_de_lignes, pathologies_distinctes, departements_distincts, annees_distinctes,
    nombre_de_cas, population_reference, prevalence_globale, prevalence_moyenne
)

def resume_global(df: pd.DataFrame) -> dict:
    """
    Génère un résumé global des données.
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