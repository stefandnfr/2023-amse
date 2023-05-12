import requests
import csv
import os.path
import sqlite3

url = "https://offenedaten-koeln.de/sites/default/files/Kompensationszahlungen_Fluege.csv"
csv_file = "data/fluege.csv"
sql_file = "data/fluege.sqlite"
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
    cur.execute("CREATE TABLE t (origin, destination , quantity, emissions);") # use your column names here

    with open(csv_file, "r") as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin,delimiter=";") # comma is default delimiter
        to_db = []
        for i in dr:
            origin = i["Flug Von"]
            dest = i["Flug Nach"]
            if len(origin) > 3:
                #print(i["Flug Von"])
                origin = origin[0:3]
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
    print("created new database with " + str(len(to_db)) + " entries.")

def deleteTempCSV():
    if os.path.isfile(csv_file):
        os.remove(csv_file)
saveCSVLocally()
convertCSVToSQL()
deleteTempCSV()