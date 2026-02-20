# 3_Analyse_territoriale.py
import pandas as pd
from core.stats_pandas import (
    stats_par_departement, moyenne_nationale, ecart_a_la_moyenne,
    top_departements, bottom_departements, z_score_prevalence, valeurs_aberrantes
)

def analyse_territoriale(df: pd.DataFrame, pathologie: str) -> dict:
    """
    Analyse par département pour une pathologie.
    """
    resultats = {}
    resultats["stats_departement"] = stats_par_departement(df, pathologie)
    resultats["moyenne_nationale"] = moyenne_nationale(df, pathologie)
    resultats["ecart_a_la_moyenne"] = ecart_a_la_moyenne(df, pathologie)
    resultats["top10_departements"] = top_departements(df, pathologie)
    resultats["bottom10_departements"] = bottom_departements(df, pathologie)
    resultats["z_score"] = z_score_prevalence(df, pathologie)
    resultats["valeurs_aberrantes"] = valeurs_aberrantes(df, pathologie)
    return resultats