import csv
import urllib.request
import random
import utils.conversion as conversion
from pathlib import Path

def charger_echantillon(n=5) -> list[dict]:
    csv_path = Path(r"C:\Users\Dell\Desktop\python\Analyse_pathologie\data\effectifs.csv")
    echantillon = []
    conv = conversion.Conversion_donnees()
    
    valid_count = 0  # compteur uniquement des lignes valides
    
    with open(csv_path, encoding="utf-8-sig") as response:
        lecteur_csv = csv.DictReader(response, delimiter=";")
        
        for l in lecteur_csv:
            # Exclusion des lignes non exploitables
            if l["patho_niv1"] == "Total consommants tous régimes":
                continue
            if l["top"] == "POP_TOT_IND":
                continue
            if not l["Ntop"] or not l["prev"]:
                continue
            if l["dept"] == "999":
                continue 
            
            try:
                departement = conv.departement(l["dept"])
                pathologie, niveau_patho = conv.pathologie(l)
                ligne_convertie = {
                    "Annee": int(l["annee"]),
                    "Pathologie": pathologie,
                    "Niveau_pathologie": niveau_patho,
                    "Age": l["libelle_classe_age"],
                    "Sexe": l["libelle_sexe"],
                    "Code_departement": l["dept"].strip().upper(),
                    "Departement": departement,
                    "Ntop": int(l["Ntop"]),
                    "Npop": int(l["Npop"]),
                    "prev": float(l["prev"])
                }
            except ValueError:
                continue
            
            # Reservoir sampling sur les lignes valides
            if valid_count < n:
                echantillon.append(ligne_convertie)
            else:
                j = random.randint(0, valid_count)
                if j < n:
                    echantillon[j] = ligne_convertie
            
            valid_count += 1  # on incrémente seulement pour les lignes valides

    return echantillon
