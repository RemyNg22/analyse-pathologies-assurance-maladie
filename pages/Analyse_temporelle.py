# 4_Analyse_temporelle.py
import pandas as pd
from core.stats_pandas import (
    stats_par_annee, variation_annuelle, tendance_generale, pente_tendance,
    moyenne_nationale_annee, z_score_prevalence_annee, annees_anormales
)

def analyse_temporelle(df: pd.DataFrame, pathologie: str) -> dict:
    """
    Analyse temporelle pour une pathologie.
    """
    resultats = {}
    resultats["stats_par_annee"] = stats_par_annee(df, pathologie)
    resultats["variation_annuelle"] = variation_annuelle(df, pathologie)
    resultats["tendance_generale"] = tendance_generale(df, pathologie)
    resultats["pente_tendance"] = pente_tendance(df, pathologie)
    resultats["moyenne_nationale_annee"] = moyenne_nationale_annee(df, pathologie)
    resultats["z_score_annee"] = z_score_prevalence_annee(df, pathologie)
    resultats["annees_anormales"] = annees_anormales(df, pathologie)
    return resultats