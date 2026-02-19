

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



def tendance_generale(donnees: list[dict], pathologie: str) -> str | None:
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

    :param donnees: données de santé nettoyées
    :param pathologie: pathologie étudiée
    :return: "hausse", "baisse", "stable" ou None
    """
    variations = variation_annuelle(donnees, pathologie)

    if not variations:
        return None

    cumul_diff_absolue = 0
    nb_annee = 0

    for variation in variations.values():
        diff = variation.get("difference absolue")

        if diff is not None:
            cumul_diff_absolue += diff
            nb_annee += 1

    if nb_annee == 0:
        return None

    moyenne_variation = cumul_diff_absolue / nb_annee

    if moyenne_variation > 0:
        return "hausse"
    elif moyenne_variation < 0:
        return "baisse"
    else:
        return "stable"
    


def pente_tendance(donnees: list[dict], pathologie: str) -> float | None:
    """
    Retourne la moyenne d'évolution annuelle de la prévalence entre
    la première année d'observation et la dernière année.

    :param donnees: données de santé nettoyées
    :param pathologie: nom de la pathologie étudiée
    :return: pente annuelle (float) ou None
    """
    
    donnee_patho = filtrer_par_pathologie(donnees, pathologie)
    stats_annee = stats_par_annee(donnees, pathologie)
    
    if len(stats_annee.keys()) < 2:
        return None

    premiere_annee = min(stats_annee.keys())
    derniere_annee = max(stats_annee.keys())

    donnees_prem_annee = filtrer_par_annee(donnee_patho, premiere_annee)
    donnees_dern_annee = filtrer_par_annee(donnee_patho, derniere_annee)

    prev_prem_annee = prevalence_globale(donnees_prem_annee)
    prev_dern_annee = prevalence_globale(donnees_dern_annee)
    
    duree = derniere_annee - premiere_annee

    if duree == 0:
        return None

    pente = (prev_dern_annee - prev_prem_annee) / duree

    return round(pente, 3)


def stats_par_departement(donnees: list[dict], pathologie: str) -> dict:
    """
    Calcule les statistiques descriptives par département
    pour une pathologie donnée.
    """
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    resultats = {}

    codes_departements = {d["Code_departement"] for d in donnees_patho}

    for code in codes_departements:
        sous_ensemble = [d for d in donnees_patho if d["Code_departement"] == code]
        stats = statistiques_descriptives(sous_ensemble)

        resultats[code] = {"Departement": sous_ensemble[0]["Departement"], **stats}

    def cle_tri(code: str):
        num = ""
        lettre = ""
        for c in code:
            if c.isdigit():
                num += c
            else:
                lettre += c
        return (int(num), lettre)

    resultats_tries = dict(sorted(resultats.items(), key=lambda x: cle_tri(x[0])))

    return resultats_tries



def classement_departements(donnees: list[dict], pathologie: str) -> list[tuple]:
    """
    Classement par département de la prévalence globale, de la plus petite à la plus grande
    """
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    depts_distincts = departements_distincts(donnees_patho)

    resultats = []

    for dept in depts_distincts:
        sous_ensemble = filtrer_par_departement(donnees_patho, dept)
        prev = prevalence_globale(sous_ensemble)

        if prev is not None:
            resultats.append((dept, prev))

    resultats_tries = sorted(resultats, key=lambda x: x[1])

    classement = [(rang + 1, dept, prev) for rang, (dept, prev) in enumerate(resultats_tries)]

    return classement


def moyenne_nationale(donnees: list[dict], pathologie: str) -> float | None:
    """
    Calcule la prévalence nationale pondérée pour une pathologie (total_ntop / total_npop).
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)

    total_ntop = 0
    total_npop = 0

    for ligne in donnees_patho:
        total_ntop += ligne["Ntop"]
        total_npop += ligne["Npop"]

    if total_npop == 0:
        return None

    prevalence_nationale = (total_ntop / total_npop) * 100

    return round(prevalence_nationale, 3)



def ecart_a_la_moyenne(donnees: list[dict], pathologie: str) -> list[tuple]:
    """
    Calcul pour chaque département l'écart à la moyenne calculée dans la fonction
    moyenne_nationale pour une pathologie (prévalence globale départementale - prévalence nationale)
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    depts_distincts = departements_distincts(donnees_patho)
    
    moyenne_nat = moyenne_nationale(donnees, pathologie)

    resultats = []


    for dept in depts_distincts:
        sous_ensemble = filtrer_par_departement(donnees_patho, dept)
        prev = prevalence_globale(sous_ensemble)

        if prev is not None:
            ecart = round(prev - moyenne_nat, 3)
            resultats.append((dept, ecart))

    resultats_tries = sorted(resultats, key=lambda x: x[1])

    return resultats_tries


def bottom_departements(donnees: list[dict], pathologie: str) -> list[tuple] | None:
    """
    Renvoie les 10 départements avec la prévalence la plus faible pour une pathologie donnée
    """

    classement = classement_departements(donnees, pathologie)

    if classement is None:
        return None

    return classement[:10]


def top_departements(donnees: list[dict], pathologie: str) -> list[tuple] | None:
    """
    Renvoie les 10 départements avec la prévalence la plus forte pour une pathologie donnée
    """

    classement = classement_departements(donnees, pathologie)

    if classement is None:
        return None

    top10 = classement[-10:][::-1]

    nouveau_classement = [
        (rang + 1, dept, prev)
        for rang, (_, dept, prev) in enumerate(top10)
    ]

    return nouveau_classement



def z_score_prevalence(donnees: list[dict], pathologie: str) -> list[tuple] | None:
    """
    Calcule le z-score pour chaque département et retourne une liste triée par ordre croissant
    (attention, c'est un z-score sur un cumul de toutes les années étudiées)
    """
    
    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    depts_distincts = departements_distincts(donnees_patho)

    moyenne_nat = moyenne_nationale(donnees, pathologie)

    list_prev = []

    for dept in depts_distincts:
        sous_ensemble = filtrer_par_departement(donnees_patho, dept)
        prev = prevalence_globale(sous_ensemble)

        if prev is not None:
            list_prev.append((dept, prev))

    nb_valeurs = len(list_prev)

    if nb_valeurs < 2:
        return None

    #Calcul écart-type
    somme_ecarts_carres = sum((prev - moyenne_nat) ** 2 for dept, prev in list_prev)

    ecart_type = (somme_ecarts_carres / (nb_valeurs - 1)) ** 0.5

    #Calcul z-score + arrondi
    resultats = [(dept, round((prev - moyenne_nat) / ecart_type, 3)) for dept, prev in list_prev]


    resultats_tries = sorted(resultats, key=lambda x: x[1])

    return resultats_tries


def valeurs_aberrantes(donnees: list[dict], pathologie: str, seuil=2) -> list[tuple] :
    """
    Retourne les départements ayant une valeur aberrante, soit une valeur de z-score égale ou dépassant le seuil de 2 ou -2
    (attention, le z-score est calculé sur un cumul de toutes les années étudiées)
    """

    liste_z_score = z_score_prevalence(donnees, pathologie)

    if not liste_z_score:
        return []
    
    resultats = []
    
    for dept, z_score in liste_z_score:
        if z_score <= -seuil or z_score >= seuil:
            resultats.append((dept, z_score))

    return resultats



def stats_par_departement_annee(donnees, pathologie) -> list[tuple[int, dict]]:
    """
    Calcule les statistiques descriptives par département et par année pour une pathologie donnée.
    """

    resultats_par_annee = {}

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    annees_differentes = sorted(annees_distinctes(donnees_patho), key=int)

    codes_departements = {d["Code_departement"] for d in donnees_patho}

    def cle_tri(code: str):
        num = ""
        lettre = ""
        for c in code:
            if c.isdigit():
                num += c
            else:
                lettre += c
        return (int(num), lettre)

    for annee in annees_differentes:

        resultats_par_dept = {}

        sous_ensemble_annee = filtrer_par_annee(donnees_patho, annee)

        for code in codes_departements:

            sous_ensemble_dept = [d for d in sous_ensemble_annee if d["Code_departement"] == code]

            if not sous_ensemble_dept:
                continue

            stats = statistiques_descriptives(sous_ensemble_dept)

            resultats_par_dept[code] = {
                "Departement": sous_ensemble_dept[0]["Departement"], **stats}

        resultats_tries_dept = dict(sorted(resultats_par_dept.items(), key=lambda x: cle_tri(x[0])))

        resultats_par_annee[annee] = resultats_tries_dept

    return sorted(resultats_par_annee.items(), key=lambda x: int(x[0]))



def moyenne_nationale_annee(donnees: list[dict], pathologie: str) -> dict:
    """
    Calcule la prévalence nationale pondérée par année (somme Ntop / somme Npop * 100).
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    annees_dist = annees_distinctes(donnees_patho)
    
    resultats = {}

    for annee in annees_dist:
        sous_ensemble = filtrer_par_annee(donnees_patho, annee)

        total_ntop = 0
        total_npop = 0
        
        for ligne in sous_ensemble:
            total_ntop += ligne["Ntop"]
            total_npop += ligne["Npop"]
    
            if total_npop == 0:
                resultats[annee] = None

        resultats[annee] = round((total_ntop / total_npop) * 100, 3)

    return resultats



def z_score_prevalence_annee(donnees: list[dict], pathologie: str) -> dict | None:
    """
    Calcule le z-score de la prévalence pour chaque département et par année.
    Retourne un dictionnaire trié par z-score croissant.
    """

    donnees_patho = filtrer_par_pathologie(donnees, pathologie)
    depts_distincts = departements_distincts(donnees_patho)

    moyenne_nat = moyenne_nationale_annee(donnees, pathologie)

    if not moyenne_nat:
        return None

    z_score_prev_annee = {}

    for annee in moyenne_nat.keys():

        sous_ensemble_annee = filtrer_par_annee(donnees_patho, annee)
        list_prev = []

        for dept in depts_distincts:
            sous_ensemble_dept = filtrer_par_departement(sous_ensemble_annee, dept)
            prev = prevalence_globale(sous_ensemble_dept)

            if prev is not None:
                list_prev.append((dept, prev))

        nb_valeurs = len(list_prev)

        if nb_valeurs < 2:
            z_score_prev_annee[annee] = None
            continue

        moyenne = moyenne_nat[annee]

        somme_ecarts_carres = sum((prev - moyenne) ** 2 for _, prev in list_prev)
        ecart_type = (somme_ecarts_carres / (nb_valeurs - 1)) ** 0.5

        if ecart_type == 0:
            z_score_prev_annee[annee] = None
            continue

        resultats = [(dept, round((prev - moyenne) / ecart_type, 3)) for dept, prev in list_prev]

        resultats.sort(key=lambda x: x[1])

        z_score_prev_annee[annee] = resultats

    return z_score_prev_annee



def annees_anormales(donnees: list[dict], pathologie: str, seuil=2) -> list[dict]:
    """
    Retourne les années aberrantes, c'est-à-dire les années où la moyenne absolue des z-scores (ensemble des départements)
    est supérieur ou égale à 2 par rapport à la moyenne nationale pour une pathologie.
    """

    z_score_prev = z_score_prevalence_annee(donnees, pathologie)
    annees_aberrantes = []

    for annee, dept_z_score in z_score_prev.items():
        if not dept_z_score: 
            continue

        
        moyenne_abs = sum(abs(z) for _, z in dept_z_score) / len(dept_z_score)
        if moyenne_abs >= seuil:
            annees_aberrantes.append({annee: round(moyenne_abs, 3)})

    return annees_aberrantes



def top_pathologies(donnees: list[dict], *, 
                    sexe=None,
                    age= None,
                    departement=None,
                    annee=None,
                    top_n=None) -> list[tuple]:
    """
    Calcule le classement des pathologies selon une dimension donnée, avec possibilité de filtrer 
    par sexe, age, département et/ou année. Possibilité de selectionner le nombre de pathologie
    avec la prévalence la plus forte via le paramètre top_n.
    """

    filtrage = filtrer_multi_criteres(
        donnees,
        sexe=sexe,
        age=age,
        departement=departement,
        annee=annee
    )

    agregation = {}

    for ligne in filtrage:
        patho = ligne["Pathologie"]

        if patho not in agregation:
            agregation[patho] = {"ntop": 0, "npop": 0}

        agregation[patho]["ntop"] += ligne["Ntop"]
        agregation[patho]["npop"] += ligne["Npop"]

    resultats = []

    for patho, valeurs in agregation.items():
        
        if valeurs["npop"] == 0:
            prevalence = 0.0
            
        else:
            prevalence = round((valeurs["ntop"] / valeurs["npop"]) * 100,3)

        resultats.append((patho, prevalence))

    resultats_tries = sorted(resultats, key=lambda x: x[1], reverse=True)

    if top_n is not None:
        return resultats_tries[:top_n]

    return resultats_tries



def pathologies_croissance_forte(donnees: list[dict],
                                 annee_depart: int,
                                 annee_arrivee: int,
                                 sexe: str | None = None,
                                 age: str | None = None,
                                 departement: str | None = None,
                                 top_n: int | None = None) -> list[tuple] | None:
    """
    Retourne les pathologies avec la croissance la plus forte entre une année de départ et
    une année d'arrivée. Retourne la croissance absolue entre la prévalence annuelle de de deux années.
    Le tri est fait par croissance décroissante.
    """
    filtrage = filtrer_multi_criteres(
        donnees,
        sexe=sexe,
        age=age,
        departement=departement,
    )

    if not filtrage:
        return None

    if annee_depart is None or annee_arrivee is None:
        return None

    if annee_depart > annee_arrivee:
        return None

    annee_dep = {}
    annee_arr = {}

    
    for ligne in filtrage:
        patho = ligne["Pathologie"]
        annee = ligne["Annee"]
        ntop = ligne["Ntop"]
        npop = ligne["Npop"]

        if annee == annee_depart:
            if patho not in annee_dep:
                annee_dep[patho] = {"ntop": 0, "npop": 0}
                
            annee_dep[patho]["ntop"] += ntop
            annee_dep[patho]["npop"] += npop

        elif annee == annee_arrivee:
            if patho not in annee_arr:
                annee_arr[patho] = {"ntop": 0, "npop": 0}
                
            annee_arr[patho]["ntop"] += ntop
            annee_arr[patho]["npop"] += npop

    
    resultats = []

    for patho in annee_dep:
        if patho in annee_arr:

            ntop_dep = annee_dep[patho]["ntop"]
            npop_dep = annee_dep[patho]["npop"]

            ntop_arr = annee_arr[patho]["ntop"]
            npop_arr = annee_arr[patho]["npop"]

            if npop_dep > 0 and npop_arr > 0:

                prev_dep = (ntop_dep / npop_dep) * 100
                prev_arr = (ntop_arr / npop_arr) * 100

                croissance = round(prev_arr - prev_dep, 3)

                resultats.append((patho, croissance))


    resultats.sort(key=lambda x: x[1], reverse=True)


    if top_n is not None:
        resultats = resultats[:top_n]

    return resultats



def resume_global_avance(donnees: list[dict],
                             sexe: str | None = None,
                             age: str | None = None,
                             departement: str | None = None,
                             annee: int | None = None) -> dict | None:
    """
    Résumé analytique avancé pour dashboard. Permet un filtrage ou non. Calcule 
    la somme de Ntop, Npop, la prévalence globale, le nombre de pathologies, années, la pathologie n°1,
    le département le plus touché, et plusieurs autres informations utiles. Retourne un dict avec les informations
    pour être utilisé dans streamlit

    """

    # FILTRAGE
    filtre = []

    for ligne in donnees:
        if sexe and ligne["Sexe"] != sexe:
            continue
        if age and ligne["Age"] != age:
            continue
        if departement and ligne["Departement"] != departement:
            continue
        if annee and ligne["Annee"] != annee:
            continue
        filtre.append(ligne)

    if not filtre:
        return None

    # VARIABLES
    total_ntop = 0
    total_npop = 0

    patho_dict = {}
    dep_dict = {}
    annee_dict = {}

    annees_uniques = set()
    pathologies_uniques = set()
    departements_uniques = set()

    # AGRÉGATION
    for ligne in filtre:
        patho = ligne["Pathologie"]
        dep = ligne["Departement"]
        an = ligne["Annee"]
        ntop = ligne["Ntop"]
        npop = ligne["Npop"]

        total_ntop += ntop
        total_npop += npop

        annees_uniques.add(an)
        pathologies_uniques.add(patho)
        departements_uniques.add(dep)

        # Pathologie
        if patho not in patho_dict:
            patho_dict[patho] = {"ntop": 0, "npop": 0}
            
        patho_dict[patho]["ntop"] += ntop
        patho_dict[patho]["npop"] += npop

        # Département
        if dep not in dep_dict:
            dep_dict[dep] = {"ntop": 0, "npop": 0}
            
        dep_dict[dep]["ntop"] += ntop
        dep_dict[dep]["npop"] += npop

        # Année
        if an not in annee_dict:
            annee_dict[an] = {"ntop": 0, "npop": 0}
            
        annee_dict[an]["ntop"] += ntop
        annee_dict[an]["npop"] += npop

    # PRÉVALENCE GLOBALE
    prevalence_globale = (round((total_ntop / total_npop) * 100, 3) if total_npop != 0 else 0.0)

    # PATHOLOGIE TOP
    patho_top = None
    patho_top_val = -1

    for p, valeurs in patho_dict.items():
        if valeurs["npop"] > 0:
            prev = (valeurs["ntop"] / valeurs["npop"]) * 100
            
            if prev > patho_top_val:
                patho_top_val = prev
                patho_top = p

    patho_top_val = round(patho_top_val, 3)

    # DEPARTEMENT TOP
    dep_top = None
    dep_top_val = -1

    for d, valeurs in dep_dict.items():
        if valeurs["npop"] > 0:
            prev = (valeurs["ntop"] / valeurs["npop"]) * 100
            
            if prev > dep_top_val:
                dep_top_val = prev
                dep_top = d

    dep_top_val = round(dep_top_val, 3)

    # ANNEE CRITIQUE
    annee_critique = None
    annee_critique_val = -1

    # Pour calcul tendance
    liste_prevalences = []

    for a in sorted(annee_dict):
        valeurs = annee_dict[a]
        
        if valeurs["npop"] > 0:
            prev = (valeurs["ntop"] / valeurs["npop"]) * 100
            liste_prevalences.append(prev)

            if prev > annee_critique_val:
                annee_critique_val = prev
                annee_critique = a

    annee_critique_val = round(annee_critique_val, 3)

    # TENDANCE MOYENNE
    tendance = None

    if len(liste_prevalences) > 1:
        differences = []
        
        for i in range(1, len(liste_prevalences)):
            differences.append(liste_prevalences[i] - liste_prevalences[i - 1])
            
        tendance = round(sum(differences) / len(differences), 3)

    # RESULTAT FINAL
    return {
        "nb_lignes": len(filtre),
        "nb_pathologies": len(pathologies_uniques),
        "nb_departements": len(departements_uniques),
        "nb_annees": len(annees_uniques),

        "total_cas": total_ntop,
        "population_totale": total_npop,
        "prevalence_globale": prevalence_globale,

        "pathologie_plus_prevalente": patho_top,
        "prevalence_pathologie_top": patho_top_val,

        "departement_plus_impacte": dep_top,
        "prevalence_departement_top": dep_top_val,

        "annee_plus_critique": annee_critique,
        "prevalence_annee_critique": annee_critique_val,

        "tendance_moyenne_annuelle": tendance
    }
