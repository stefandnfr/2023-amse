import requests
import csv
import os.path
import sqlite3


url = "https://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV"
csv_file = "data/train_stations.csv"
sql_file = "data/train_stations.sqlite"
def saveCSVLocally():
    r = requests.get(url, allow_redirects=True)
    open(csv_file,"wb").write(r.content)

def convertCSVToSQL():
    if os.path.exists(sql_file):

        confirmation = input("Are you sure you want to delete the old database? (no backup will be made) \n(y/n): ")
        if confirmation.lower() == "y":
            os.remove(sql_file)
            print("old database deleted successfully.")
        else:
            print("Deletion cancelled. Not fetching new data")
            return
    else:
        print("Database does not exist. Fetching new one...")
    con = sqlite3.connect(sql_file)
    cur = con.cursor()
    cur.execute("CREATE TABLE t (evanr, name);") # use your column names here

    with open(csv_file, "r", encoding="utf-8") as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin,delimiter=";") # comma is default delimiter
        to_db = [(i["EVA_NR"], i["NAME"]) for i in dr]

    cur.executemany("INSERT INTO t (evanr, name) VALUES (?,?);", to_db)
    con.commit()
    con.close()
    print("created new database with " + str(len(to_db)) + " entries.")

def deleteTempCSV():
    if os.path.isfile(csv_file):
        os.remove(csv_file)
saveCSVLocally()
convertCSVToSQL()
deleteTempCSV()