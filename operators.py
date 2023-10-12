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
    'name':'Free',
    'code':'free',
    'url': 'https://mobile.free.fr/account/antennes-relais-indisponibles.csv',
    'type': 'csv',
    'separator': ',',
    'skipheader':0,
    'skipfooter': 0,
    'structure':{ # Table de renommage des champs pour harmonisation entre opérateurs
      'Dpt'       : 'departement',
      'cp'        : 'code_postal',
      'localite'  : 'commune',
      'latitude'  : 'lat',
      'longitude' : 'long',
      'Voix'      : 'voix',
      'Data'      : 'data'
    },
    'reformatting':{}
  },
  {
    'name':'Orange',
    'code':'orange',
    'url': 'https://couverture-mobile.orange.fr/mapV3/siteshs/data/Liste_des_antennes_provisoirement_hors_service.csv',
    'encoding':'windows-1250',
    'type': 'csv',
    'separator': ';',
    'skipheader':2,
    'skipfooter': 0,
    'structure':{
      "Département"          : 'departement',
      "Commune"              : 'commune',
      "Latitude"             : 'lat',
      "Longitude"            : 'long',
      "Service Voix / SMS 2G": 'voix2g',
      "Service Voix / SMS 3G": 'voix3g',
      "Service Voix / SMS 4G": 'voix4g',
      "Service de données 3G": 'data3g',
      "Service de données 4G": 'data4g',
      "Service de données 5G": 'data5g',
      "Antenne-relais gérée par Orange": 'propre',
      "Date et heure début panne ou maintenance antenne-relais pour le Service Voix / SMS": 'debut_voix',
      "Date de rétablissement prévue pour le Service Voix / SMS": 'fin_voix',
      "Date et heure début panne ou maintenance antenne-relais pour le Service de données": 'debut_data',
      "Date de rétablissement prévue pour le Service de données": 'fin_data'
    },
    # Table de reformattage des champs (typiquement les dates).
    # 'match'  désigne un motif (expression régulière) utilisé pour filtrer le champs fourni par l'opérateur
    # 'format' désigne le nouveau format à appliquer au filtrage trouvé
    'reformatting':{ 
        'debut_voix':{'match':'([0-9]{2})/([0-9]{2})/([0-9]{4}) ([0-9]{2}):([0-9]{2}):([0-9]{2})' , 'format':'{2}-{1}-{0} {3}:{4}:{5}'},
        'debut_data':{'match':'([0-9]{2})/([0-9]{2})/([0-9]{4}) ([0-9]{2}):([0-9]{2}):([0-9]{2})' , 'format':'{2}-{1}-{0} {3}:{4}:{5}'},
        'fin_voix'  :{'match':'([0-9]{2})/([0-9]{2})/([0-9]{4})' , 'format':'{2}-{1}-{0}'},
        'fin_data'  :{'match':'([0-9]{2})/([0-9]{2})/([0-9]{4})' , 'format':'{2}-{1}-{0}'},
    }
  },
  {
    'name':'SFR',
    'code':'sfr',
    'url': 'https://static.s-sfr.fr/media/export-arcep/siteshorsservices.csv',
    'type': 'csv',
    'separator': ';',
    'skipheader':3,
    'skipfooter': 8,
    'structure':{
      "Departement"       : 'departement',
      "code_insee_commune": 'code_insee',
      "Commune"           : 'commune',
      "X_WGS84_GPS"       : 'lat',
      "Y_WGS84_GPS"       : 'long',
      "Voix/SMS"          : 'voix',
      "internet mobile"   : 'data'
    },
    'reformatting':{}
  },
  {
    'name':'Bouygues Telecom',
    'code':'bytel',
    'url': 'https://www.bouyguestelecom.fr/static/com/assets/reseau/siteshs/downloads/antennesindisponibles.csv',
    'type': 'csv',
    'separator': ';',
    'skipheader':0,
    'skipfooter': 0,
    'structure':{
      "Code SI"    : 'code_site',
      "Commune"    : 'commune',
      "Code INSEE" : 'code_insee',
      "Lat"        : 'lat',
      "Lon"        : 'long',
      "2Gvoix"     : 'voix2g',
      "3Gvoix"     : 'voix3g',
      "3Gdata"     : 'data3g',
      "4Gdata"     : 'data4g',
      "5Gdata"     : 'data5g',
      "voix"       : 'voix',
      "data"       : 'data',
      "raison"     : 'raison',
      "détail"     : 'detail',
      "début"      : 'debut',
    },
    'reformatting':{
        'debut':{'match':'(.*)' , 'format':'{0}'},
        'fin'  :{'match':'([0-9\-]*) (.*)' , 'format':'{0}'},
    }
  }
]

# Les noms des champs récupérés
status_columns   = ['voix2g','voix3g','voix4g','data3g','data4g','data5g','voix','data']
equipment_columns   = status_columns + ['propre','detail']
detail_duree_columns= ['debut_voix','fin_voix','debut_data','fin_data','debut','fin']
indispo_columns     = ['region','departement','code_postal','code_insee','commune','lat','long']
all_columns = ['date','operateur','op_code'] + indispo_columns + equipment_columns + detail_duree_columns
