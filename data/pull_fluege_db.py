import csv
import os.path
import sqlite3
import sys
from .utils import saveCSVLocally,removeOldDBIfExists


def convertCSVToSQL(verbose, csv_path, sql_path ):
    con = sqlite3.connect(sql_path)
    cur = con.cursor()
    cur.execute("CREATE TABLE t (origin, destination , quantity, emissions);") # use your column names here
    with open(csv_path, "r") as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin,delimiter=";") # comma is default delimiter
        to_db = []
        for i in dr:
            origin = i["Flug Von"]
            dest = i["Flug Nach"]

            if len(origin) > 3:
                continue
            if len(dest)>3:
                dest = dest[0:3]

            # manually fix error of wrong airport code in excel
            if dest == "FR " or dest == "FR" or dest == " FR":
                dest = "FRA"
            #discard other non three alphanumeric names
            if len(origin) != 3 or len(dest) != 3 or not origin.isalpha() or not dest.isalpha():
                continue

            to_db.append((origin, dest, i["Anz. Flug"], i["CO2-Wert"]))


    cur.executemany("INSERT INTO t (origin, destination , quantity, emissions) VALUES (?, ?, ?, ?);", to_db)
    con.commit()
    con.close()
    if verbose:
        print("created new database 'fluege.sqlite' with " + str(len(to_db)) + " entries.")


def pull_fluege_db(verbose):

    url = "https://offenedaten-koeln.de/sites/default/files/Kompensationszahlungen_Fluege.csv"
    csv_file = "data/fluege.csv"
    sql_file = "data/fluege.sqlite"

    saveCSVLocally(csv_file,url)
    removeOldDBIfExists(sql_file, verbose, requires_confirmation=False)                     
    convertCSVToSQL(verbose, csv_file,sql_file)
    if os.path.isfile(csv_file):
        os.remove(csv_file)

