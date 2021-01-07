# Enregistrement de l'historique des sites mobiles en pannes tous opérateurs

## Contexte

Dans le cadre des accords du [New Deal Mobile](https://arcep.fr/cartes-et-donnees/tableau-de-bord-du-new-deal-mobile.html#NetworkStatus), les quatre opérateurs (Orange, Free, SFR et Bouygues Telecom) sont tenus de publier chaque jour un fichier qui répertorie leur sites actuellement indisponibles.

Ces données sont actuellement délivrées dans un format brut (souvent sans visualisation), sans historique (analyse temporelle impossible) et dans des formats différents (analyse comparative difficile).

Afin de faciliter l'utilisation de ces sources de données, l'Arcep a donc développé un script de récupération et d'harmonisation des données qu'elle met ici à disposition.

Une [cartorgaphie minimaliste](https://ARCEP-dev.github.io/siteshs/index.html) est également mise à disposition et permet de visualiser un historique de ces pannes.

## Contacts

- Gaspard FEREY (Arcep) - gaspard [point] ferey [chez] arcep [point] fr
- Romain MAZIERE (Arcep) - romain [point] maziere [chez] arcep [point] fr

## Open Data

Les données ne sont pas encore publiées en opendata.

## Données sources

Les fichiers publiées par les opérateurs:

| Opérateur        | URL |
|------------------|-----|
| Free             | https://mobile.free.fr/account/antennes-relais-indisponibles.csv |
| Orange           | https://couverture-mobile.orange.fr/mapV3/siteshs/data/Liste_des_antennes_provisoirement_hors_service.csv |
| SFR              | https://static.s-sfr.fr/media/export-arcep/siteshorsservices.csv |
| Bouygues Telecom | http://antennesindisponibles.bouyguestelecom.fr/antennesindisponibles.xls |

## Langages

- [Python3](https://www.python.org/)

## Bibliothèques

- [GeoPandas](https://geopandas.org)


## Utilisation

Utiliser Python3 pour exécuter le fichier `siteshs.py` avec le chemin d'export comme premier paramètre:

```bash
python3 siteshs.py /export/path/
```

## Installation en tant que job cron

- Sous Linux, simplement ajouter la ligne suivante dans votre fichier [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html):
```bash
13 6 * * * root python3 /path/to/repo/siteshs.py /export/path/ >> /var/log/cron.log 2>&1
```
