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


from os import path, mkdir, sep
from operators import operateurs


def create_if_not_exists(folder):
    if not path.isdir(folder):
        mkdir(folder)

# L'achitecture de fichiers est la suivante:
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
# Les dossiers sont créés à l'initialisation s'ils sont inexistants               
class PathHandler:
    def __init__(self, root, date):
        self.root = root
        self.default_date = date
        create_if_not_exists(self.root+sep+'all')
        create_if_not_exists(self.root+sep+'all'+sep+date)
        # Création d'un répertoire par opérateur
        for op in operateurs:
            create_if_not_exists(self.root+sep+op['name'])
            create_if_not_exists(self.op_folder(op,date))

    def date(self, date):
        return date if date else self.default_date
    def op_folder(self, op, date=None):
        return self.root+sep+op['name']+sep+self.date(date)
    def op_path(self, op, suffix, date=None):
        return self.op_folder(op,date)+sep+self.date(date)+'_'+op['name']+suffix
    def all_path(self, suffix, date=None):
        return self.root+sep+'all'+sep+self.date(date)+sep+self.date(date)[0:10]+suffix
    def raw_path(self, op, date=None):
        return self.op_path(op,'_raw.'+op['type'],date)
