# 5_Anomalies.py
import pandas as pd
from core.stats_pandas import valeurs_aberrantes, annees_anormales

def anomalies(df: pd.DataFrame, pathologie: str, seuil: float = 2) -> dict:
    """
    Retourne les anomalies territoriales et temporelles pour une pathologie.
    """
    return {
        "departements_aberrants": valeurs_aberrantes(df, pathologie, seuil),
        "annees_aberrantes": annees_anormales(df, pathologie, seuil)
    }