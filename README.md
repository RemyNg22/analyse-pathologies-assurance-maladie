# Analyse des pathologies – Assurance Maladie (France)

Ce projet a pour objectif d’analyser les **effectifs de patients pris en charge par pathologie** en France, à partir des données ouvertes de l’Assurance Maladie (CNAM), selon le **sexe**, la **classe d’âge**, l’**année** et le **territoire** (département).

Le projet est volontairement construit en **deux approches** :
- une approche en **Python pur** (listes de dictionnaires)
- une approche avec **pandas** (DataFrame, parquet)

Le projet est **en cours de développement**.  
Certaines fonctionnalités et visualisations sont prévues mais pas encore implémentées.

---

## Jeu de données

**Source** : data.gouv.fr – Cartographie des pathologies et des dépenses de l’Assurance Maladie.

Les données décrivent les effectifs de patients pris en charge par l’ensemble des régimes d’assurance maladie, selon :
- la pathologie, le traitement chronique ou l’épisode de soins
- le sexe
- la classe d’âge
- le territoire (département, région)
- l’année (2015 à 2023)

### Catégories de pathologies (exemples)

- maladies cardioneurovasculaires  
- diabète  
- cancers  
- pathologies psychiatriques  
- maladies neurologiques  
- maladies respiratoires chroniques  
- maladies inflammatoires ou rares (dont VIH)  
- insuffisance rénale chronique terminale  
- hospitalisations (dont Covid-19 à partir de 2020)  
- maternité  
- traitements antalgiques ou anti-inflammatoires  
- etc.

La **prévalence** correspond à la proportion (%) de patients pris en charge pour une pathologie donnée, rapportée à la population de référence de l’Assurance Maladie.

---

## Population de référence

La population de la cartographie regroupe l’ensemble des bénéficiaires de l’assurance maladie obligatoire ayant :
- bénéficié d’au moins une prestation remboursée dans l’année
- et/ou séjourné au moins une fois dans un établissement de santé

En 2024, cela représente **67,4 millions de bénéficiaires**.

---

## Secret statistique

Conformément à la loi du 7 juin 1951 :
- aucun effectif inférieur à **11 patients** n’est diffusé
- ces valeurs sont indiquées comme **NS (Non significatif)** dans les données sources

---

## Pré-requis

- Python 3.10+
- pandas
- numpy (si utilisé)
- streamlit (pour l’interface future)


## Structure du projet

Analyse_pathologie/

```text
Analyse_pathologie/
│
├── core/
│   ├── stats_python.py         # Statistiques en Python pur
│   └── stats_pandas.py         # Statistiques avec Pandas
│
├── utils/
│   └── conversion.py           # Fonctions de conversion (départements, etc.)
│
├── data/
│   └── effectifs.parquet       # Données au format Parquet
│
├── notebooks/
│   ├── demo_pandas.ipynb       # Notebook de démonstration Pandas (à faire)
│   └── demo_pure_python.ipynb  # Notebook de démonstration Python pur (à faire)
│
├── Test_LOADER_CSV.py          # Tests sur échantillon (à supprimer plus tard)
├── Test_STATS_PYTHON.py        # Tests sur échantillon (à supprimer plus tard)
├── Test_STATS_PANDAS.py        # Tests sur échantillon (à supprimer plus tard)
│
├── app.py                      # Application Streamlit (à faire)
│
├── requirements.txt
└── README.md
```


## À propos du loader CSV

Une fonction `charger_effectifs()` permet de **télécharger directement le fichier CSV depuis data.gouv.fr**.

 **Attention** :
- le fichier CSV fait environ **850 Mo**
- le chargement est **lent** et **consommateur de mémoire**

 **Il est fortement recommandé d’utiliser la version pandas avec le fichier `parquet`**, déjà placé dans le dossier `data/`.

---

## Version pandas (recommandée)

La version pandas :
- lit les données depuis `data/effectifs.parquet`
- est plus rapide
- est plus adaptée aux analyses statistiques et futures visualisations

### Exemple de lancement

```bash
python Test_STATS_PANDAS.py

ou

python -m core.stats_pandas #depuis racine du projet
```|
