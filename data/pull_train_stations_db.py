import requests
import csv
import os.path
import sqlite3
from .utils import saveCSVLocally,removeOldDBIfExists


def convertCSVToSQL(csv_path,sql_path):
    con = sqlite3.connect(sql_path)
    cur = con.cursor()
    cur.execute("CREATE TABLE t (evanr, name, long, lat);") # use your column names here

    with open(csv_path, "r", encoding="utf-8") as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin,delimiter=";") # comma is default delimiter
        to_db = [(i["EVA_NR"], i["NAME"], i["Laenge"],i["Breite"]) for i in dr]

    cur.executemany("INSERT INTO t (evanr, name, long, lat) VALUES (?,?,?,?);", to_db)
    con.commit()
    con.close()
    print("created new database with " + str(len(to_db)) + " entries.")


def pull_train_stations():
    url = "https://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV"
    csv_file = "data/train_stations.csv"
    sql_file = "data/train_stations.sqlite"
    saveCSVLocally(csv_file,url)
    removeOldDBIfExists(sql_file,requires_confirmation=False)
    convertCSVToSQL(csv_file,sql_file)
    if os.path.exists(csv_file):
        os.remove(csv_file)
        
