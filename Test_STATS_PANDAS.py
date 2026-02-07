import pandas as pd
import utils.conversion as conversion
from pathlib import Path

def charger_effectifs() -> pd.DataFrame:
    """
    Charge le fichier effectifs.parquet qui est une conversion en parquet du fichier effectif.csv
    disponible sur data.gouv, puis filtre et nettoie les données avec la bibliothèque pandas
    """

    parquet_path = Path(r"C:\Users\Dell\Desktop\python\Analyse_pathologie\data\effectifs.parquet")
    
    #Initialisation des en-têtes pour le tableau
    colonnes_entete = ['annee', 
                       'patho_niv1',
                       'patho_niv2',
                       'patho_niv3', 
                       'libelle_classe_age', 
                       'libelle_sexe', 
                       'dept', 
                       'top',
                       'Ntop', 
                       'Npop', 
                       'prev',
                       ]

    df = pd.read_parquet(parquet_path, columns=colonnes_entete)
    
    #Enlève les espaces inutiles
    df.columns = df.columns.str.strip()


    #Verifie que les données suivantes sont numériques
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")
    df["Ntop"] = pd.to_numeric(df["Ntop"], errors="coerce")
    df["Npop"] = pd.to_numeric(df["Npop"], errors="coerce")
    df["prev"] = pd.to_numeric(df["prev"], errors="coerce")



    #Exclusion des lignes agrégées non exploitables
    df = df[
        ~(
            df["patho_niv1"].str.contains("Total consommants tous régimes", na=False) |
            df["patho_niv2"].str.contains("Total consommants tous régimes", na=False) |
            df["patho_niv3"].str.contains("Total consommants tous régimes", na=False)
        )
    ]
    df = df[df["top"] != "POP_TOT_IND"]
    df = df[df["dept"] != "999"]

    """
    Crée la colonne ``pathologie`` en utilisant le niveau de pathologie
    le plus précis disponible :
    - ``patho_niv3`` si renseigné
    - sinon ``patho_niv2``
    - sinon ``patho_niv1``
    """
    df["pathologie"] = (
        df["patho_niv3"].fillna("").str.strip()
    )

    df.loc[df["pathologie"] == "", "pathologie"] = (
        df["patho_niv2"].fillna("").str.strip()
    )

    df.loc[df["pathologie"] == "", "pathologie"] = (
        df["patho_niv1"].fillna("").str.strip()
    )


    conv = conversion.Conversion_donnees()
    
    #Application de la conversion des numéros de département -> nom de département
    df["departement"] = df["dept"].apply(conv.departement)
    

    df = df.drop("dept", axis=1)
    df = df.drop(columns=["top"])
    df = df.drop(columns=["patho_niv1", "patho_niv2", "patho_niv3"])


    #Suppression des lignes avec données manquantes
    df = df.dropna(subset=["annee", "pathologie", "Ntop", "prev"])

    df = df.astype({
        "annee": int,
        "Ntop": int,
        "Npop": int,
        "prev": float
    })

    # Ne plus utiliser la notation scientifique, pour plus de lisibilité
    pd.set_option('display.float_format', '{:,.3f}'.format)

    return df


def nombre_de_lignes(df: pd.DataFrame) -> int:
    """
    Retourne le nombre total d'enregistrements dans les données.

    :param df: DataFrame Pandas
    :return: nombre total de lignes
    """
    return len(df)


def pathologies_distinctes(df: pd.DataFrame) -> int:
    """
    Retourne le nombre des pathologies distinctes présentes dans les données.

    :param df: DataFrame Pandas
    :return: nombre des différents noms de traitements (pathologies)
    """
    return df["pathologie"].nunique()


def departements_distincts(df: pd.DataFrame) -> int:
    """
    Retourne le nombre des départements distincts présents dans les données.

    :param df: DataFrame Pandas
    :return: nombre de départements distincts
    """
    return df["departement"].nunique()


def annees_distinctes(df: pd.DataFrame) -> int:
    """
    Retourne le nombre d'années distinctes présentes dans les données.

    :param df: DataFrame Pandas
    :return: nombre d'années distinctes
    """
    return df["annee"].nunique()


def nombre_de_cas(df: pd.DataFrame) -> int:
    """
    Calcule le nombre total de cas observés (somme des Ntop).

    :param df: DataFrame Pandas
    :return: nombre total de cas
    """
    return df["Ntop"].sum()


def population_reference(df: pd.DataFrame) -> int:
    """
    Calcule la population totale de référence (somme des Npop).

    :param df: DataFrame Pandas
    :return: population totale
    """
    return df["Npop"].sum()


def prevalence_globale(df: pd.DataFrame) -> float:
    """
    Calcule la prévalence globale en pourcentage sur l'ensemble des données.

    Formule :
        (total des cas / population totale) * 100

    :param df: DataFrame Pandas
    :return: prévalence globale (%) arrondie à 3 décimales
    """
    total_cas = df["Ntop"].sum()
    total_population = df["Npop"].sum()
    if total_population == 0:
        return 0.0
    return round((total_cas / total_population) * 100, 3)        


def prevalence_moyenne(df: pd.DataFrame) -> float:
    """
    Calcule la moyenne arithmétique des prévalences individuelles non nulles.

    Attention :
    - cette valeur n'est pas pondérée par la population
    - elle ne représente pas la prévalence globale

    :param df: DataFrame Pandas
    :return: prévalence moyenne (%) arrondie à 3 décimales
    """
    prev_moy_valeur = df.loc[df["prev"] != 0, "prev"]
    return round(prev_moy_valeur.mean(), 3) if not prev_moy_valeur.empty else 0.0



def stats_patho(df: pd.DataFrame, 
                pathologie: str,
                sexe: str | None = None,
                age: str | None = None,
                departement: str | None = None,
                annee: int | None = None
                ) -> pd.Series:

    """
    Calcule des statistiques descriptives de prévalence pour une pathologie donnée,
    avec filtres optionnels (sexe, âge, département, année).

    Statistiques calculées :
    - nombre total de cas
    - population totale
    - prévalence moyenne
    - médiane
    - minimum
    - maximum
    - écart-type (échantillon)

    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :param sexe: filtre optionnel sur le sexe
    :param age: filtre optionnel sur la classe d'âge
    :param departement: filtre optionnel sur le département
    :param annee: filtre optionnel sur l'année
    :return: Series Pandas contenant les statistiques agrégées
        pour la pathologie filtrée
    """

    # Filtrage selon les critères
    df_filtre = df[df["pathologie"] == pathologie]

    if sexe is not None:
        df_filtre = df_filtre[df_filtre["libelle_sexe"] == sexe]
    if age is not None:
        df_filtre = df_filtre[df_filtre["libelle_classe_age"] == age]
    if departement is not None:
        df_filtre = df_filtre[df_filtre["departement"] == departement]
    if annee is not None:
        df_filtre = df_filtre[df_filtre["annee"] == annee]

    # Si le filtrage donne un DataFrame vide, renvoyer un Series rempli de 0
    if df_filtre.empty:
        return pd.Series({
            "Ntop_totale": 0,
            "Npop_totale": 0,
            "prevalence_moyenne": 0.0,
            "prevalence_mediane": 0.0,
            "prevalence_min": 0.0,
            "prevalence_max": 0.0,
            "ecart_type": 0.0,
            "prevalence_globale": 0.0
        })

    # Calcul des statistiques
    Ntop_totale = df_filtre["Ntop"].sum()
    Npop_totale = df_filtre["Npop"].sum()
    prevalence_moyenne = df_filtre["prev"].mean()
    prevalence_mediane = df_filtre["prev"].median()
    prevalence_min = df_filtre["prev"].min()
    prevalence_max = df_filtre["prev"].max()
    ecart_type = df_filtre["prev"].std()
    prevalence_globale = (Ntop_totale / Npop_totale * 100) if Npop_totale > 0 else 0.0

    # Retourne un Series avec arrondi à 3 décimales
    return pd.Series({
        "Ntop_totale": Ntop_totale,
        "Npop_totale": Npop_totale,
        "prevalence_moyenne": round(prevalence_moyenne, 3),
        "prevalence_mediane": round(prevalence_mediane, 3),
        "prevalence_min": round(prevalence_min, 3),
        "prevalence_max": round(prevalence_max, 3),
        "ecart_type": round(ecart_type, 3) if not pd.isna(ecart_type) else 0.0,
        "prevalence_globale": round(prevalence_globale, 3)
    })



def stats_par_sexe(df: pd.DataFrame, pathologie: str) -> dict:
    """
    Statistiques par sexe pour une pathologie.
    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :return: Dict Pandas retournant les stats par pathologie et par sexe
    """

    resultats = {}
    for sexe in ("hommes", "femmes"):
        # Passe le df filtré au sexe à stats_patho
        resultats[sexe] = stats_patho(df, pathologie, sexe=sexe)
    return resultats



def ratio_cas_hf(df: pd.DataFrame, pathologie: str) -> float | None:
    """
    Calcule le ratio hommes / femmes pour une pathologie donnée à partir d'un DataFrame Pandas.

    Le ratio est basé sur la somme des effectifs de patients pris en charge (Ntop) par sexe.
    Cette version réutilise la fonction stats_par_sexe pour le filtrage et l'agrégation.

    Limites :
    - Le ratio reflète un rapport d’effectifs observés et non un risque ou une
      probabilité individuelle.
    - Si aucune donnée n'est disponible pour les femmes, la fonction retourne None.

    :param df: DataFrame Pandas contenant les colonnes nécessaires
    :param pathologie: str, nom de la pathologie
    :return: float arrondi à 3 décimales ou None si non calculable
    """

    stats_hf = stats_par_sexe(df, pathologie)

    nb_hommes = stats_hf.get("hommes", {}).get("Ntop_totale", 0)
    nb_femmes = stats_hf.get("femmes", {}).get("Ntop_totale", 0)

    if nb_femmes == 0:
        return None

    return round(nb_hommes / nb_femmes, 3)


def difference_prevalence_sexe(df: pd.DataFrame, pathologie: str) -> float | None:
    """
    Calcule la différence de prévalence globale hommes - femmes pour une pathologie.

    Utilise les effectifs de patients pris en charge et renvoie None si les données 
    ne permettent pas le calcul (population nulle ou pathologie absente).

    :param df: DataFrame Pandas contenant les colonnes nécessaires
    :param pathologie: nom de la pathologie
    :return: différence de prévalence (%) arrondie à 3 décimales, ou None si non calculable
    """

    stats_hf = stats_par_sexe(df, pathologie)

    prev_glob_h = stats_hf.get("hommes", {}).get("prevalence_globale")
    prev_glob_f = stats_hf.get("femmes", {}).get("prevalence_globale")

    if prev_glob_h is None or prev_glob_f is None:
        return None

    return round(prev_glob_h - prev_glob_f, 3)



def tranches_age_distinctes_df(df: pd.DataFrame) -> list:
    """
    Retourne les tranches d'âge distinctes présentes dans un DataFrame Pandas,
    triées par ordre croissant, en excluant 'tous âges' mais en conservant
    'plus de 95 ans' à la fin.
    
    :param df: DataFrame Pandas
    :return: liste triée des tranches d'âge
    """
    tranches = [t for t in df['libelle_classe_age'].unique() if t != "tous âges"]

    def age_min(tranche: str) -> int:
        if "plus de" in tranche:
            return 999  # pour que "plus de 95 ans" soit à la fin
        start = tranche.split()[1]  # "de X à Y ans"
        return int(start)

    return sorted(tranches, key=age_min)



def stats_par_tranche_age(df: pd.DataFrame, pathologie: str) -> dict:
    """
    Statistiques par tranche d'âge pour une pathologie, en utilisant
    tranches_age_distinctes_df pour le tri.
    
    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :return: dict avec les tranches d'âge comme clés et les stats Pandas comme valeurs
    """
    resultats = {}
    df_patho = df[df['pathologie'] == pathologie]

    tranches_tries = tranches_age_distinctes_df(df_patho)

    for age in tranches_tries:
        resultats[age] = stats_patho(df_patho, pathologie, age=age)

    return resultats



#TEST DE FONCTION
tableau = charger_effectifs()
patho = tableau["pathologie"].unique()[:3]


for d in patho:
    print(stats_par_tranche_age(tableau, d))