#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Romain MAZIERE and Gaspard FEREY (ARCEP)
# Workflow to generate the shapefiles for the opendata
# Requires Python 3.7

import sys, time, math, re, json, requests
from datetime import date, datetime
import    pandas as  pd
import geopandas as gpd
from sqlalchemy import create_engine,MetaData,Table
from sqlalchemy.sql import select,delete,insert,text

from operators import operateurs
from paths import PathHandler

datename= str(date.today())

print("")
print("################################################")
print("    Lancement du script à la date du ",datename)
print("################################################")
print("")

# Chemin vers le dossier de sauvegarde
save = PathHandler( sys.argv[1], datename )


def try_download(op):
    """ Tentative de téléchargement du fichier opérateur.
    
    Renvoie True en cas de succès, False sinon.
    """
    r = requests.get(op["url"], allow_redirects=True)
    if(r.status_code != 200):
        return False
    else:
        print("Fichier téléchargé.")
        # sauvegarde sur le disque
        export_file = save.raw_path(op,datename)
        with open(export_file, 'wb') as file:
            file.write(r.content)
        print( "Sauvegardé à " + export_file)
        return True

def download(op, maxtry):
    """ Effectue maxtry tentative de téléchargement du fichier opérateur. """
    for i in range(maxtry):
        print("Tentative :",i+1)
        if try_download(op):
            print("Succès du téléchargement !")
            return True
        else:
            print("Echec de téléchargement !")
            time.sleep(5)

# Récupération des fichiers opérateur
for op in operateurs:
    print("Téléchargement de " + op['name'] + " : " + op["url"])
    download(op, 10)

def nonify(e,default=None):
    """ Transformation des NaN en None """
    return e if str(e) != 'nan' else default

def get_raw_dataframe(op):
    """ Fonction de récupération d'un dataframe brut. """
    if op["type"] == "xls":
        return pd.read_excel(save.raw_path(op,datename),
                             sheet_name= op["excelsheet"],
                             header    = op["excelheader"],
                             index_col = None)
    else:
        return pd.read_csv(save.raw_path(op,datename),
                           sep        = op["separator"],
                           skiprows   = op["skipheader"],
                           skipfooter = op["skipfooter"],
                           engine = 'python')

# Uniformisation des fichiers
for op in operateurs:
    print("Opérateur : " + op["name"])
    df = get_raw_dataframe(op)
    print("Sites HS : " + str(len(df.index)))
    
    #Renommage des colonnes
    df.rename(columns=op["structure"], inplace=True)

    header = ["date","operateur","departement","code_postal","code_insee","commune","lat","long","voix","data"]
    nf = pd.DataFrame(columns=header)
    
    if ("lat" not in df or "long" not in df):
        # Reprojection en WGS84 des coordonées projetées
        pt = gpd.GeoDataFrame(geometry=gpd.points_from_xy(df["x"], df["y"]))
        pt.crs = {"init" :"epsg:2154"}
        pts = pt.to_crs({"init": "epsg:4326"})
        nf["lat" ] = pts.geometry.y
        nf["long"] = pts.geometry.x
    else:
        nf["lat"]  = df["lat"]
        nf["long"] = df["long"]
        
    for col in ["code_insee", "code_postal"]:
        # Formatage du code postal et/ou code insee
        if col in df:
            nf[col] = df[col].astype(str).str.zfill(5)
            if "departement" not in df:
                nf["departement"] = nf[col].str[0:2]
        
    # Extraction du code département via le code postal ou le code insee
    if "departement" in df:
        if df["departement"].dtypes == "int64":
            df = df.astype({"departement": str})
        nf["departement"] = [ re.findall('([0-9][0-9AB]?).*', d)[0] for d in df["departement"] ]
    
    for col in ["commune","voix","data"]:
        nf[col] = df.get(col)
    
    # Tri des données
    nf = nf.sort_values(by=["departement", "code_insee", "code_postal"])
    nf["date"]     = datename[0:10]
    nf["operateur"]= op['name']
    
    op['dataframe'] = nf
    
    # Ecriture du fichier au format standardisé csv (Un format unique pour les gouverner tous !)
    nf.to_csv(save.op_path(op,'.csv'), sep=',', index=False)
    # Export en JSON (bon ok, deux...)
    nf.to_json(save.op_path(op,'.json'), orient="records")

union_df = pd.concat( [ op['dataframe'] for op in operateurs ])
union_df.to_csv(save.all_path('.csv'), sep=',', index=False)
union_df.to_json(save.all_path('.json'), orient="records")

# Conversion en GeoJSON
geojson_properties = ["operateur", "departement","code_postal","code_insee","commune","voix","data"]
def df_to_geojson(df, properties, lat='lat', lon='long'):
    return {
        'type':'FeatureCollection',
        'features':
            [
                {  'type':      'Feature',
                   'properties':{ prop : nonify(row[prop]) for prop in properties },
                   'geometry':  {'type':'Point',
                                 'coordinates':[row[lon],row[lat]]}}
                for _, row in df.iterrows()
            ]
    }

# Export en GeoJSON
with open(save.all_path('.geojson'), "w") as file:
    # Export dans le fichier au format geojson
    geojson = df_to_geojson(union_df, geojson_properties)
    file.write(json.dumps(geojson))

print("Fichiers de données générés !")
