# Enregistrement de l'historique des antennes en pannes tous opérateurs

## Contexte

Dans le cadre des accords du
[New Deal Mobile](https://arcep.fr/cartes-et-donnees/tableau-de-bord-du-new-deal-mobile.html#NetworkStatus),
les quatres opérateurs (Orange, Free, SFR et Bouygues Telecom) publient chaque jour un fichier
qui répertorie leur antennes actuellement indisponibles.

Ces données sont délivrées dans un format brut (pas de visualisation), sans historique (analyse temporelle impossible)
et dans des formats différents (analyse comparative difficile).
L'Arcep a donc développé un script de récupération quotidienne et d'harmonisation des données
qu'elle met ici à disposition.

Une [cartorgaphie minimaliste](https://ARCEP-dev.github.io/siteshs/index.html) est également mise à disposition
et permet de visualiser cet historique des pannes.

## Contacts

- Gaspard FEREY (Arcep) - gaspard [point] ferey [chez] arcep [point] fr
- Romain MAZIERE (Arcep) - romain [point] maziere [chez] arcep [point] fr

## Open Data

Les données ne sont pas encore publiées en opendata.

## Données sources

Les fichiers publiées par les opérateurs:

| Opérateur        | URL |
|------------------|-----|
| Free             | https://mobile.free.fr/moncompte/index.php?page=csv-antennes-relais-indisponibles |
| Orange           | https://suivi-des-incidents.orange.fr/liste_des_antennes_en_panne.csv |
| SFR              | https://static.s-sfr.fr/media/export-arcep/siteshorsservices.csv |
| Bouygues Telecom | http://antennesindisponibles.bouyguestelecom.fr/antennesindisponibles.xls |

## Langages

- [Python3](https://www.python.org/)

## Bibliothèqes

- [GeoPandas](https://geopandas.org)



## Utilisation


## Installation du job cron

- Simplement ajouter la ligne suivante dans votre fichier crontab:
```bash
13 6 * * * root python3 /siteshs.py /dumps/ >> /var/log/cron.log 2>&1
```
