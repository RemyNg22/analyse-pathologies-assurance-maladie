import csv
import utils.conversion as conversion
import urllib.request
import utils.conversion as conversion


def charger_effectifs() -> list[dict]:

    """
    Charge le fichier effectifs.csv depuis data.gouv.fr
    et retourne une liste de dictionnaires nettoyés.
    """

    url = "https://www.data.gouv.fr/api/1/datasets/r/5f71ba43-afc8-43a0-b306-dafe29940f9c"

    #les données sont enregistrées ici
    donnees = []
    conv = conversion.Conversion_donnees()

    with urllib.request.urlopen(url) as response:
        lignes = response.read().decode("utf-8-sig").splitlines()
        lecteur_csv = csv.DictReader(lignes, delimiter=";")

    
        for l in lecteur_csv:

            #Exlusion des lignes agrégées non exploitables
            if l["patho_niv1"] == "Total consommants tous régimes":
                continue

            if l["top"] == "POP_TOT_IND":
                continue

            if l["dept"] == "999":
                continue 

            #Exclusion des lignes incomplètes
            if not l["Ntop"] or not l["prev"]:
                continue
            
            try:
                

                departement = conv.departement(l["dept"])
                pathologie, niveau_patho = conv.pathologie(l)

                donnees.append({
                    "Annee" : int(l["annee"]),
                    "Pathologie": pathologie,
                    "Niveau_pathologie": niveau_patho,
                    "Age" : l["libelle_classe_age"],
                    "Sexe" : l["libelle_sexe"],
                    "Departement" : departement,
                    "Ntop": int(l["Ntop"]),
                    "Npop": int(l["Npop"]),
                    "prev": float(l["prev"])
                })

            except ValueError:
                #Ignore les lignes avec données non convertibles
                continue

    return donnees
