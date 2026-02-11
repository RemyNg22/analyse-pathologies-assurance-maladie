

def nombre_de_lignes(donnees: list[dict]) -> int:
    """
    Retourne le nombre total d'enregistrements dans les données.

    :param donnees: liste de dictionnaires représentant les lignes du fichier
    :return: nombre total de lignes
    """    
    return len(donnees)


def pathologies_distinctes(donnees: list[dict]) -> set:
    """
    Retourne l'ensemble des pathologies distinctes présentes dans les données.

    :param donnees: liste de dictionnaires
    :return: set des noms de traitements (pathologies)
    """
    return set(d["Pathologie"] for d in donnees)


def tranches_age_distinctes(donnees: list[dict]) -> list:
    """
    Retourne les tranches d'âge distinctes présentes dans les données,
    triées par ordre croissant, en excluant 'tous âges' mais en conservant
    'plus de 95 ans' à la fin.

    :param donnees: liste de dictionnaires
    :return: liste triée des tranches d'âge
    """
    
    tranches = [d["Age"] for d in donnees if d["Age"] != "tous âges"]

    # Fonction pour extraire l'âge minimum d'une tranche
    def age_min(tranche: str) -> int:
        if "plus de" in tranche:
            return 999  # Met "plus de 95 ans" à la fin
        start = tranche.split()[1] 
        return int(start)

    tranches_tries = sorted(tranches, key=age_min)

    return tranches_tries


def departements_distincts(donnees: list[dict]) -> set:
    """
    Retourne l'ensemble des départements distincts présents dans les données.

    :param donnees: liste de dictionnaires
    :return: set des départements
    """
    return set(d["Departement"] for d in donnees)



def annees_distinctes(donnees: list[dict]) -> set:
    """
    Retourne l'ensemble des années distinctes présentes dans les données.

    :param donnees: liste de dictionnaires
    :return: set des années
    """
    return set(d["Annee"] for d in donnees)



def nombre_de_cas(donnees: list[dict]) -> int:
    """
    Calcule le nombre total de cas observés (somme des Ntop).

    :param donnees: liste de dictionnaires
    :return: nombre total de cas
    """
    return sum(d["Ntop"] for d in donnees)



def population_reference(donnees: list[dict]) -> int:
    """
    Calcule la population totale de référence (somme des Npop).

    :param donnees: liste de dictionnaires
    :return: population totale
    """
    return sum(d["Npop"] for d in donnees)



def prevalence_globale(donnees: list[dict]) -> float:
    """
    Calcule la prévalence globale en pourcentage sur l'ensemble des données.

    Formule :
        (total des cas / population totale) * 100

    :param donnees: liste de dictionnaires
    :return: prévalence globale (%) arrondie à 3 décimales
    """
    total_cas = nombre_de_cas(donnees)
    total_population = population_reference(donnees)

    if total_population == 0:
        return 0.0
    
    return round((total_cas / total_population) * 100, 3)



def prevalence_moyenne(donnees: list[dict]) -> float:
    """
    Calcule la moyenne arithmétique des prévalences individuelles non nulles.

    Attention :
    - cette valeur n'est pas pondérée par la population
    - elle ne représente pas la prévalence globale

    :param donnees: liste de dictionnaires
    :return: prévalence moyenne (%) arrondie à 3 décimales
    """
    valeur_prev = [d["prev"] for d in donnees if d["prev"] != 0]
    return round(sum(valeur_prev) / len(valeur_prev) if valeur_prev else 0, 3)



def filtrer_par_pathologie(donnees : list[dict], pathologie : str) -> list[dict]:
    return [d for d in donnees if d["Pathologie"] == pathologie]

def filtrer_par_sexe(donnees : list[dict], sexe: str) -> list[dict]:
    return [d for d in donnees if d["Sexe"] == sexe]

def filtrer_par_age(donnees : list[dict], age: str) -> list[dict]:
    return [d for d in donnees if d["Age"] == age]

def filtrer_par_departement(donnees : list[dict], departement: str) -> list[dict]:
    return [d for d in donnees if d["Departement"] == departement]

def filtrer_par_annee(donnees : list[dict], annee: int) -> list[dict]:
    return [d for d in donnees if d["Annee"] == annee]


def filtrer_multi_criteres(donnees : list[dict],
                           pathologie=None,
                           sexe=None,
                           age=None,
                           departement=None,
                           annee= None) -> list[dict]:
    
    result = donnees

    if pathologie is not None:
        result = filtrer_par_pathologie(result, pathologie)

    if sexe is not  None:
        result = filtrer_par_sexe(result, sexe)

    if age is not None:
        result = filtrer_par_age(result, age)

    if departement is not None:
        result = filtrer_par_departement(result, departement)

    if annee is not None:
        result = filtrer_par_annee(result, annee)

    return result




def statistiques_descriptives(donnees : list[dict]) -> dict | None:
    """
    Calcule des statistiques descriptives de prévalence :

    Statistiques calculées :
    - nombre total de cas
    - population totale
    - prévalence moyenne
    - médiane
    - minimum
    - maximum
    - écart-type (échantillon)

    :param donnees: liste de dictionnaires
    :return: dictionnaire de statistiques ou None si aucune donnée exploitable
    """

    if not donnees:
        return None
    
    # Agrégats principaux
    Ntop_totale = sum(d["Ntop"] for d in donnees)
    Npop_totale = sum(d["Npop"] for d in donnees)

    prevalence_valeur = [d["prev"] for d in donnees if d["prev"] != 0]
    if not prevalence_valeur:
        return None
    
    # Statistiques descriptives
    prev_moyenne = sum(prevalence_valeur) / len(prevalence_valeur)
    prev_min = min(prevalence_valeur)
    prev_max = max(prevalence_valeur)

    prev_tri = sorted(prevalence_valeur)
    prev_nombre_valeur = len(prev_tri)
    prev_mid = prev_nombre_valeur // 2

    # Médiane
    if prev_nombre_valeur%2 == 0:
        prev_mediane = (prev_tri[prev_mid - 1] + prev_tri[prev_mid]) / 2
    else:
        prev_mediane = prev_tri[prev_mid]

    # Écart-type (échantillon)
    if prev_nombre_valeur < 2 :
        prev_ecart_type = 0.0
    else:
        prev_variance = sum((d - prev_moyenne) ** 2 for d in prevalence_valeur) / (prev_nombre_valeur - 1)
        prev_ecart_type = prev_variance ** 0.5


    return {
        "Ntop totale" : Ntop_totale,
        "Npop totale" : Npop_totale,
        "Prevalence moyenne" : round(prev_moyenne, 3),
        "Prevalence mediane" : round(prev_mediane, 3),
        "Prevalence min" : round(prev_min, 3),
        "Prevalence max" : round(prev_max, 3),
        "Ecart-type prevalence" : round(prev_ecart_type, 3)
    }    



def stats_par_sexe(donnees: list[dict], pathologie: str) -> dict:
    """
    Calcule les statistiques descriptives par sexe (H / F)
    pour une pathologie donnée.
    """
    resultats = {}

    # On filtre d'abord par pathologie
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    for sexe in ("hommes", "femmes"):
        sous_ensemble = filtrer_par_sexe(donnees_patho, sexe)
        stats = statistiques_descriptives(sous_ensemble)
        resultats[sexe] = stats

    return resultats



def ratio_cas_hf(donnees: list[dict], pathologie: str) -> float | None:
    """
    Calcule le ratio hommes / femmes pour une pathologie donnée.
    
    Le ratio est calculé à partir des effectifs de patients pris en charge (Ntop),
    agrégés par sexe, pour une pathologie donnée.
    
    Choix méthodologiques :
    - Le calcul repose sur la colonne Ntop, car les données de prévalence (prev)
      sont incomplètes et hétérogènes selon les territoires et niveaux d’agrégation.
    - La pathologie est définie par priorité :
      patho_niv3 -> patho_niv2 -> patho_niv1.
    - Les lignes correspondant à des agrégats non exploitables
      (ex. "tous sexes", totaux nationaux, départements 999) doivent être exclues
      en amont ou filtrées dans la fonction.
    
    Limites d’interprétation :
    - Le ratio reflète un rapport d’effectifs observés et non un risque ou une
      probabilité individuelle.
    - En présence de données manquantes ou faiblement renseignées pour un sexe,
      le ratio peut être biaisé ou non calculable.
    
    :param donnees: liste de dictionnaires
    :param pathologie: str
    :return: float ou None si données non exploitables
    """
    
        
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    stats_hf = {}

    for sexe in ("hommes", "femmes"):
        sous_ensemble = filtrer_par_sexe(donnees_patho, sexe)
        nb_cas = nombre_de_cas(sous_ensemble)
        stats_hf[sexe] = nb_cas

    if stats_hf["femmes"] == 0:
        return None
            
    return round(stats_hf["hommes"] / stats_hf["femmes"], 3)



def difference_prevalence_sexe(donnees: list[dict], pathologie: str) -> float | None:
    """
    Calcule la différence de prévalence globale entre les hommes et les femmes
    pour une pathologie donnée.

    Formule :
        prévalence hommes − prévalence femmes

    Une valeur positive indique une prévalence plus élevée chez les hommes,
    une valeur négative chez les femmes.

    :param donnees: liste de dictionnaires
    :param pathologie: pathologie étudiée
    :return: différence de prévalence en points de pourcentage, ou None si non calculable
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    donnees_h = filtrer_par_sexe(donnees_patho, "hommes")
    donnees_f = filtrer_par_sexe(donnees_patho, "femmes")

    if population_reference(donnees_h) == 0 or population_reference(donnees_f) == 0:
        return None

    prevalence_glob_h = prevalence_globale(donnees_h)
    prevalence_glob_f = prevalence_globale(donnees_f)

    return round(prevalence_glob_h - prevalence_glob_f, 3)



def stats_par_tranche_age(donnees: list[dict], pathologie: str) -> dict:
    """
    Calcule les statistiques descriptives par tranche d'age
    pour une pathologie donnée.
    """
    
    resultats = {}
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    tranches_age_differentes = tranches_age_distinctes(donnees_patho)
    
    for age in tranches_age_differentes:
        sous_ensemble = filtrer_par_age(donnees_patho, age)
        stats = statistiques_descriptives(sous_ensemble)
        resultats[age] = stats

    return resultats


def variation_prevalence_entre_ages(
    donnees: list[dict],
    pathologie: str,
    tranche_age_1: str,
    tranche_age_2: str
) -> float | None:
    """
    Calcule la variation de prévalence entre deux tranches d'âge
    pour une pathologie donnée.
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    donnees_tranche_1 = filtrer_par_age(donnees_patho, tranche_age_1)
    donnees_tranche_2 = filtrer_par_age(donnees_patho, tranche_age_2)

    if not donnees_tranche_1 or not donnees_tranche_2:
        return None

    prev_1 = prevalence_globale(donnees_tranche_1)
    prev_2 = prevalence_globale(donnees_tranche_2)

    return prev_2 - prev_1



def age_central_pathologie(donnees: list[dict], pathologie: str) -> tuple | None:
    """
    Retourne la tranche d'âge pour laquelle la prévalence de la pathologie
    est la plus élevée et sa valeur.
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    if not donnees_patho:
        return None

    resultats = {}

    for age in tranches_age_distinctes(donnees_patho):
        sous_ensemble = filtrer_par_age(donnees_patho, age)
        resultats[age] = prevalence_globale(sous_ensemble)

    tranche_max = max(resultats, key=resultats.get)
    return tranche_max, resultats[tranche_max]



def stats_par_annee(donnees:list[dict], pathologie: str) -> dict:
    """
    Calcule les statistiques descriptives par année
    pour une pathologie donnée.
    """
    
    resultats = {}
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    annees_differentes = annees_distinctes(donnees_patho)
    
    for annee in annees_differentes:
        sous_ensemble = filtrer_par_annee(donnees_patho, annee)
        stats = statistiques_descriptives(sous_ensemble)
        resultats[annee] = stats

    return dict(sorted(resultats.items()))


def variation_annuelle(donnees: list[dict], pathologie: str) -> dict:
    """
    Calcule la variation annuelle de la prévalence globale pour une pathologie donnée.

    Pour chaque année (à partir de la deuxième), retourne :
    - la différence absolue de prévalence par rapport à l'année précédente
    - la variation relative en pourcentage

    Si la prévalence de l'année précédente est nulle, la variation relative est None.

    :param donnees: données de santé nettoyées
    :param pathologie: pathologie étudiée
    :return: variations annuelles de la prévalence
    """
    prev_par_annee = {}

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    annees_differentes = sorted(annees_distinctes(donnees_patho))

    for annee in annees_differentes:
        sous_ensemble = filtrer_par_annee(donnees_patho, annee)
        prev_par_annee[annee] = prevalence_globale(sous_ensemble)

    variation = {}

    for i in range(1, len(annees_differentes)):
        annee = annees_differentes[i]
        annee_prec = annees_differentes[i - 1]

        diff_abs = round(
            prev_par_annee[annee] - prev_par_annee[annee_prec],
            3
        )


        if prev_par_annee[annee_prec] == 0:
            val_rel = None
        else:
            val_rel = round(
                (diff_abs / prev_par_annee[annee_prec]) * 100,
                3
            )

        variation[annee] = {
            "difference absolue": diff_abs,
            "valeur relative": val_rel
        }

    return variation