# 2_Analyse_Pathologies.py
import pandas as pd
from core.stats_pandas import stats_patho, stats_par_sexe, stats_par_tranche_age, age_central_pathologie

def analyse_pathologie(df: pd.DataFrame, pathologie: str) -> dict:
    """
    Analyse globale et par sexe/tranche d'âge pour une pathologie.
    """
    resultats = {}
    resultats["stats_globales"] = stats_patho(df, pathologie).to_dict()
    resultats["stats_par_sexe"] = stats_par_sexe(df, pathologie)
    resultats["stats_par_age"] = stats_par_tranche_age(df, pathologie)
    resultats["age_central"] = age_central_pathologie(df, pathologie)
    return resultats