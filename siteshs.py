#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Romain MAZIERE and Gaspard FEREY (ARCEP)
# Workflow to generate the shapefiles for the opendata
# Requires Python 3.7

from os import path, mkdir, sep
import sys, time, math, re, json, requests
from datetime import date, datetime
import    pandas as  pd
import geopandas as gpd

from operators import operateurs

datename= str(date.today())

print("")
print("################################################")
print("    Lancement du script à la date du ",datename)
print("################################################")
print("")

# Chemin vers le dossier de sauvegarde
savepath = sys.argv[1]
# L'achitecture est la suivante (les dossiers sont créés s'ils sont inexistants):
# savepath
#   free
#     01-01-2021
#       01-01-2021_free.csv
#       01-01-2021_free.json
#       01-01-2021_free_raw.csv  (fichier téléchargé)
#     ...                        (idem pour chaque date)
#   ...                          (idem pour chaque operateur)
#   all
#     01-01-2021                 
#       01-01-2021.csv           (fichier tout opérateurs concaténés)
#       01-01-2021.json          (fichier tout opérateurs concaténés)
#     ...                        

def op_folder(op,date):
    return savepath+sep+op['name']+sep+date
def op_path(op,date,suffix):
    return op_folder(op,date)+sep+date+'_'+op['name']+suffix
def all_path(date,suffix):
    return savepath+sep+'all'+sep+date+sep+date[0:10]+suffix
def raw_path(op,date):
    return op_path(op,date,'_raw.'+op['type'])

def create_if_not_exists(folder):
    if not path.isdir(folder):
        mkdir(folder)

create_if_not_exists(savepath+sep+'all')
create_if_not_exists(savepath+sep+'all'+sep+datename)
# Création d'un répertoire par opérateur
for op in operateurs:
    create_if_not_exists(savepath+sep+op['name'])
    create_if_not_exists(op_folder(op,datename))


def try_download(op):
    r = requests.get(op["url"], allow_redirects=True)
    if(r.status_code != 200):
        return False
    else:
        print("Fichier téléchargé.")
        # sauvegarde sur le disque
        export_file = raw_path(op,datename)
        open(export_file,"wb").write(r.content)
        print( "Sauvegardé à " + export_file)
        return True

def download(op, maxtry):
    for i in range(maxtry):
        print("Tentative :",i+1)
        if try_download(op):
            print("Succès du téléchargement !")
            return True
        else:
            print("Echec de téléchargement !")
            time.sleep(5)

# Pour chaque opérateur de la liste :
for op in operateurs:
    print("Téléchargement de " + op['name'] + " : " + op["url"])
    download(op, 10)

# Transformation des NaN en None
def nonify(e):
    return e if str(e) != 'nan' else None

# Fonction de récupération d'un dataframe brut
def get_raw_dataframe(op):
    if op["type"] == "xls":
        return pd.read_excel(raw_path(op,datename),
                             sheet_name= op["excelsheet"],
                             header    = op["excelheader"],
                             index_col = None)
    else:
        return pd.read_csv(raw_path(op,datename),
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
    nf.to_csv(op_path(op,datename,'.csv'), sep=',', index=False)
    # Export en JSON (bon ok, deux...)
    nf.to_json(op_path(op,datename,'.json'), orient="records")

union_df = pd.concat( [ op['dataframe'] for op in operateurs ])
union_df.to_csv(all_path(datename,'.csv'), sep=',', index=False)
union_df.to_json(all_path(datename,'.json'), orient="records")

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
with open(all_path(datename,'.geojson'), "w") as file:
    # Export dans le fichier au format geojson
    geojson = df_to_geojson(union_df, geojson_properties)
    file.write(json.dumps(geojson))

print("Fichiers de données générés !")
