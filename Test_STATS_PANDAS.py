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

    # Conversion du code département en str et suppression espaces
    df["dept"] = df["dept"].astype(str).str.strip()

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
    
    df_filtre = df[df["pathologie"] == pathologie]
    if sexe: df_filtre = df_filtre[df_filtre["libelle_sexe"] == sexe]
    if age: df_filtre = df_filtre[df_filtre["libelle_classe_age"] == age]
    if departement: df_filtre = df_filtre[df_filtre["departement"] == departement]
    if annee: df_filtre = df_filtre[df_filtre["annee"] == annee]

    if df_filtre.empty:
        return pd.Series({
            "Ntop_totale": 0, "Npop_totale": 0,
            "prevalence_globale": 0.0,
            "prevalence_moyenne": 0.0, "prevalence_mediane": 0.0,
            "prevalence_min": 0.0, "prevalence_max": 0.0, "ecart_type": 0.0
        })

    Ntop_totale = df_filtre["Ntop"].sum()
    Npop_totale = df_filtre["Npop"].sum()
    prev_globale = (Ntop_totale / Npop_totale * 100) if Npop_totale else 0
    prev = df_filtre["prev"]
    
    return pd.Series({
        "Ntop_totale": Ntop_totale,
        "Npop_totale": Npop_totale,
        "prevalence_globale": round(prev_globale, 3),
        "prevalence_moyenne": round(prev.mean(), 3),
        "prevalence_mediane": round(prev.median(), 3),
        "prevalence_min": round(prev.min(), 3),
        "prevalence_max": round(prev.max(), 3),
        "ecart_type": round(prev.std(), 3)
    })



def stats_par_sexe(df: pd.DataFrame, pathologie: str) -> pd.DataFrame:
    """
    Statistiques par sexe pour une pathologie.
    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :return: DataFrame Pandas retournant les stats par pathologie et par sexe
    """
    df_filtre = df[(df['pathologie'] == pathologie) & (df['libelle_sexe'] != 'tous sexes')]
    if df_filtre.empty:
        return pd.DataFrame()

    resultats = []
    for sexe, groupe in df_filtre.groupby('libelle_sexe'):
        Ntop_totale = groupe['Ntop'].sum()
        Npop_totale = groupe['Npop'].sum()
        prevalence_globale = (Ntop_totale / Npop_totale * 100) if Npop_totale else 0
        resultats.append({
            'sexe': sexe,
            'Ntop_totale': Ntop_totale,
            'Npop_totale': Npop_totale,
            'prevalence_globale': round(prevalence_globale, 3),
            'prevalence_moyenne': round(groupe['prev'].mean(), 3),
            'prevalence_mediane': round(groupe['prev'].median(), 3),
            'prevalence_min': round(groupe['prev'].min(), 3),
            'prevalence_max': round(groupe['prev'].max(), 3),
            'ecart_type': round(groupe['prev'].std(), 3)
        })
    
    return pd.DataFrame(resultats).set_index('sexe')



def ratio_cas_hf(df: pd.DataFrame, pathologie: str) -> float | None:
    """
    Calcule le ratio hommes / femmes pour une pathologie donnée à partir d'un DataFrame Pandas.

    Le ratio est basé sur la somme des effectifs de patients pris en charge (Ntop) par sexe.

    Limites :
    - Le ratio reflète un rapport d’effectifs observés et non un risque ou une
      probabilité individuelle.
    - Si aucune donnée n'est disponible pour les femmes, la fonction retourne None.

    :param df: DataFrame Pandas contenant les colonnes nécessaires
    :param pathologie: str, nom de la pathologie
    :return: float arrondi à 3 décimales ou None si non calculable
    """
    df_filtre = df[(df['pathologie'] == pathologie) & (df['libelle_sexe'] != 'tous sexes')]
    stats_hf = df_filtre.groupby('libelle_sexe')['Ntop'].sum()
    if 'hommes' not in stats_hf or 'femmes' not in stats_hf or stats_hf['femmes'] == 0:
        return None
    return round(stats_hf['hommes'] / stats_hf['femmes'], 3)


def difference_prevalence_sexe(df: pd.DataFrame, pathologie: str) -> float | None:
    """
    Calcule la différence de prévalence globale hommes - femmes pour une pathologie.

    Utilise les effectifs de patients pris en charge et renvoie None si les données 
    ne permettent pas le calcul (population nulle ou pathologie absente).

    :param df: DataFrame Pandas contenant les colonnes nécessaires
    :param pathologie: nom de la pathologie
    :return: différence de prévalence (%) arrondie à 3 décimales, ou None si non calculable
    """
    df_filtre = df[(df['pathologie'] == pathologie) & (df['libelle_sexe'].str.lower() != 'tous sexes')]
    
    stats_hf = df_filtre.groupby(df_filtre['libelle_sexe'].str.lower())[["Ntop", "Npop"]].sum()
    
    if 'hommes' not in stats_hf.index or 'femmes' not in stats_hf.index:
        return None
    if stats_hf.loc['hommes', 'Npop'] == 0 or stats_hf.loc['femmes', 'Npop'] == 0:
        return None
    
    prev_h = stats_hf.loc['hommes', 'Ntop'] / stats_hf.loc['hommes', 'Npop'] * 100
    prev_f = stats_hf.loc['femmes', 'Ntop'] / stats_hf.loc['femmes', 'Npop'] * 100
    return round(prev_h - prev_f, 3)



def stats_par_tranche_age(df: pd.DataFrame, pathologie: str) -> pd.DataFrame:
    """
    Statistiques par tranche d'âge pour une pathologie.
    
    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :return: DataFrame Pandas avec les tranches d'âge en lignes et les statistiques en colonnes
    """
    df_filtre = df[df["pathologie"] == pathologie].copy()
    if df_filtre.empty:
        return pd.DataFrame()

    conv = conversion.Conversion_donnees()
    
    df_filtre["libelle_classe_age"] = pd.Categorical(
        df_filtre["libelle_classe_age"],
        categories=conv.ordre_tranches_age(), ordered=True)
    
    df_filtre = df_filtre.sort_values("libelle_classe_age")


    stats = (
        df_filtre
        .groupby("libelle_classe_age", sort=True, observed=True)
        .agg(Ntop_totale=("Ntop", "sum"), Npop_totale=("Npop", "sum"),)
    )

    stats["prevalence_globale"] = (stats["Ntop_totale"] / stats["Npop_totale"]) * 100

    stats.loc[stats["Npop_totale"] == 0, "prevalence_globale"] = None

    return stats.round(3)


def difference_prevalence_age(df: pd.DataFrame,
                              pathologie: str,
                              tranche_age_1: str,
                              tranche_age_2: str) -> float | None:
    """
    Calcule la différence de prévalence globale entre deux tranches d'âge
    pour une pathologie donnée, selon l'ordre fourni :

    différence = prévalence(tranche_age_1) - prévalence(tranche_age_2)

    Renvoie None si l'une des tranches ou la pathologie est absente.
    """

    stats_tranche_age = stats_par_tranche_age(df, pathologie)


    if tranche_age_1 not in stats_tranche_age.index or tranche_age_2 not in stats_tranche_age.index:
        return None

    prev_t1 = stats_tranche_age.loc[tranche_age_1, "prevalence_globale"]
    prev_t2 = stats_tranche_age.loc[tranche_age_2, "prevalence_globale"]

    if prev_t1 is None or prev_t2 is None:
        return None

    return round(prev_t1 - prev_t2, 3)


def age_central_pathologie(df: pd.DataFrame, pathologie: str) -> tuple[str, float] | None:
    """
    Retourne la tranche d'âge pour laquelle la prévalence globale
    de la pathologie est la plus élevée, ainsi que sa valeur.
    Renvoie None si la pathologie n'est pas présente.
    """
    stats_tranche_age = stats_par_tranche_age(df, pathologie)
    
    if stats_tranche_age.empty:
        return None

    tranche_max = stats_tranche_age["prevalence_globale"].idxmax()
    valeur_max = stats_tranche_age["prevalence_globale"].max()

    return tranche_max, round(valeur_max, 3)



def stats_par_annee(df: pd.DataFrame, pathologie: str) -> pd.DataFrame | None:
    """
    Statistiques par annee pour une pathologie.
    
    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :return: DataFrame Pandas avec les années en lignes et les statistiques en colonnes
    """
    df_filtre = df[df["pathologie"] == pathologie].copy()
    if df_filtre.empty:
        return pd.DataFrame()

    df_filtre = df_filtre.sort_values("annee")

    stats= (
        df_filtre
        .groupby("annee", sort=True).agg(Ntop_totale=("Ntop", "sum"), Npop_totale=("Npop", "sum"),)
    )

    stats["prevalence_globale"] = (stats["Ntop_totale"] / stats["Npop_totale"]) * 100

    stats.loc[stats["Npop_totale"] == 0, "prevalence_globale"] = None

    if stats.empty:
        return None

    return stats.round(3)


def variation_annuelle(df: pd.DataFrame, pathologie: str) -> dict:
    """
    Calcule la variation annuelle de la prévalence globale pour une pathologie donnée.

    Pour chaque année (à partir de la deuxième), retourne :
    - la différence absolue de prévalence par rapport à l'année précédente
    - la variation relative en pourcentage

    Si la prévalence de l'année précédente est nulle, la variation relative est None.

    :param df: DataFrame Pandas
    :param pathologie: nom du traitement/pathologie étudiée
    :return: dict avec pour chaque annee la difference absolue et la "valeur relative
    """

    df_patho = df[df['pathologie'] == pathologie].copy()
    if df_patho.empty:
        return None

    stats_annee = (
        df_patho.groupby('annee', sort=True)
        .agg(Ntop_totale=('Ntop', 'sum'), Npop_totale=('Npop', 'sum'))
    )
    stats_annee['prevalence_globale'] = (
        stats_annee['Ntop_totale'] / stats_annee['Npop_totale'] * 100
    )
    stats_annee.loc[stats_annee['Npop_totale'] == 0, 'prevalence_globale'] = None


    variation = {}
    prev_values = stats_annee['prevalence_globale'].tolist()
    annees = stats_annee.index.tolist()

    for i in range(1, len(annees)):
        diff_abs = round(prev_values[i] - prev_values[i-1], 3)
        if prev_values[i-1] in [0, None]:
            val_rel = None
        else:
            val_rel = round((diff_abs / prev_values[i-1]) * 100, 3)
        variation[annees[i]] = {
            "difference absolue": diff_abs,
            "valeur relative": val_rel
        }

    return variation


def tendance_generale(df: pd.DataFrame, pathologie: str) -> str | None:
    """
    Détermine la tendance générale de la prévalence globale
    d'une pathologie sur la période étudiée.

    La tendance est calculée à partir de la moyenne des variations
    annuelles absolues de prévalence :

    - moyenne > 0  → "hausse"
    - moyenne < 0  → "baisse"
    - moyenne = 0  → "stable"

    Si aucune variation ne peut être calculée (ex. une seule année
    disponible ou données absentes), la fonction retourne None.

    :param df: DataFrame Pandas
    :param pathologie: nom de la pathologie étudiée
    :return: "hausse", "baisse", "stable" ou None
    """

    variations = variation_annuelle(df, pathologie)

    if not variations:
        return None

    df_variation = pd.DataFrame(variations)

    if "difference absolue" not in df_variation.index:
        return None

    moyenne_variation = df_variation.loc["difference absolue"].dropna().mean()

    if pd.isna(moyenne_variation):
        return None

    moyenne_variation = round(moyenne_variation, 3)

    if moyenne_variation > 0:
        return "hausse"
    elif moyenne_variation < 0:
        return "baisse"
    else:
        return "stable"


def pente_tendance(df: pd.DataFrame, pathologie: str) -> float | None:
    """
    Retourne la moyenne d'évolution annuelle de la prévalence entre
    la première année d'observation et la dernière année.

    :param df: DataFrame Pandas
    :param pathologie: nom de la pathologie étudiée
    :return: pente annuelle (float) ou None
    """

    stats_annee = stats_par_annee(df, pathologie)

    if stats_annee.shape[0] < 2:
        return None

    stats_annee = stats_annee.sort_values("annee")

    annee_debut = stats_annee.index[0]
    annee_fin = stats_annee.index[-1]

    prev_debut = stats_annee.iloc[0]["prevalence_globale"]
    prev_fin = stats_annee.iloc[-1]["prevalence_globale"]

    if pd.isna(prev_debut) or pd.isna(prev_fin):
        return None

    duree = annee_fin - annee_debut

    if duree == 0:
        return None

    pente = (prev_fin - prev_debut) / duree

    return round(pente, 3)


def stats_par_departement(df: pd.DataFrame, pathologie: str) -> pd.DataFrame | None:
    """
    Calcule les statistiques descriptives par département
    pour une pathologie donnée.
    """
    df_filtre = df[df["pathologie"] == pathologie].copy()
    if df_filtre.empty:
        return pd.DataFrame()

    df_filtre = df_filtre.sort_values("dept")

    stats = (
        df_filtre
        .groupby("dept", sort=True)
        .agg(Ntop_totale=("Ntop", "sum"), Npop_totale=("Npop", "sum"))
    )

    stats["prevalence_globale"] = (stats["Ntop_totale"] / stats["Npop_totale"]) * 100
    stats.loc[stats["Npop_totale"] == 0, "prevalence_globale"] = None


    conv = conversion.Conversion_donnees()
    stats["departement_nom"] = stats.index.map(conv.departement)

    if stats.empty:
        return None

    return stats.round(3)



# Test de fonction
donnee = charger_effectifs()
patho = "Diabète"

print(stats_par_departement(donnee, patho))

