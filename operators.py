#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auteurs: Romain MAZIERE and Gaspard FEREY (Arcep)
#
# Processus de récupération des sites indisponibles de France métropolitaine
# publiés par les opérateurs et sauvegarde des données uniformisées
# aux formats CSV, JSON et GeoJSON.
# 
# Nécessite Python 3.7


# Liste des opérateurs avec les urls de téléchargement des fichiers, les formats ainsi que la correspondance des colonnes
operateurs = [
  {
    "name":"free",
    "url": "https://mobile.free.fr/account/antennes-relais-indisponibles.csv",
    "type": "csv",
    "separator": ",",
    "skipheader":0,
    "skipfooter": 0,
    "structure":{
      "Dpt"       : "departement",
      "cp"        : "code_postal",
      "localite"  : "commune",
      "latitude"  : "lat",
      "longitude" : "long",
      "Voix"      : "voix",
      "Data"      : "data"
    }
  },
  {
    "name":"orange",
    "url": "https://suivi-des-incidents.orange.fr/liste_des_antennes_en_panne.csv",
    "type": "csv",
    "separator": ";",
    "skipheader":1,
    "skipfooter": 0,
    "structure":{
      "Departement"       : "departement",
      "Commune"           : "commune",
      "Latitude"          : "lat",
      "Longitude"         : "long",
      "Service Voix/SMS"  : "voix",
      "Service de Donnees": "data"
    }
  },
  {
    "name":"sfr",
    "url": "https://static.s-sfr.fr/media/export-arcep/siteshorsservices.csv",
    "type": "csv",
    "separator": ";",
    "skipheader":3,
    "skipfooter": 8,
    "structure":{
      "Departement"       : "departement",
      "code_insee_commune": "code_insee",
      "Commune"           : "commune",
      "X_WGS84_GPS"       : "lat",
      "Y_WGS84_GPS"       : "long",
      "Voix/SMS"          : "voix",
      "internet mobile"   : "data"
    }
  },
  {
    "name":"bytel",
    "url": "http://antennesindisponibles.bouyguestelecom.fr/antennesindisponibles.xls",
    "type": "xls",
    "excelsheet": 0,
    "excelheader": 4,
    "skipheader":0,
    "skipfooter": 0,
    "structure":{
      "CODE POSTAL": "code_postal",
      "COMMUNE"    : "commune",
      "X (L93)"    : "x",
      "Y (L93)"    : "y",
      "Service Voix\n(2G et 3G Hors Service)" : "voix",
      "Service d'accès à Internet et Voix sur LTE\n(3G et 4G Hors Service)" : "data"
    }
  }
]