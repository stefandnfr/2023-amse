
# from data.utils import saveCSVLocally,removeOldDBIfExists
# from data.pull_fluege_db import convertCSVToSQL
# from data.pipeline import pipeline
# from data.utils import removeOldDBIfExists,saveCSVLocally
# from data.pull_fluege_db import convertCSVToSQL
from .context import saveCSVLocally,removeOldDBIfExists,convertCSVToSQL,pipeline
import sqlite3
import os

# ===============================================================
#                       test complete pipeline
# ===============================================================
def test_pipeline():
    pipeline(verbose=True)

    artefact = "./data/domestic_flights.sqlite"
    assert os.path.isfile(artefact)
    assert os.path.isfile("./data/fluege.sqlite")
    assert os.path.isfile("./data/train_stations.sqlite")
    assert os.path.isfile("./data/mapped_airports.json")

    # Check if final artefact has expected rows and columns
    conn = sqlite3.connect(artefact)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM t")
    row_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA table_info(t)")
    column_count = len(cursor.fetchall())

    cursor.close()
    conn.close()

    # expecting at least one row == one domestic flight entry
    assert (row_count > 0)

    # expecting 10 columns: 
    # (origin, origin_long, origin_lat, destination, dest_long, dest_lat, train_origin, train_dest, quantity, emissions)
    assert (column_count == 10)


# ================================================================
#                       test utils helper function
# ================================================================

def test_saveCSVlocally_checkIfExists():
    path = "example.csv"
    saveCSVLocally(path, "")
    assert os.path.isfile(path)
    os.remove(path)

def test_removeOldDBIfExists():
    # checking if exists when there is a sqlite file
    sql_path = "example.sqlite"
    removeOldDBIfExists(sql_path, verbose=True, requires_confirmation= False)
    assert not os.path.exists(sql_path)

    #now checking if there isnt one
    removeOldDBIfExists(sql_path, verbose=True, requires_confirmation=False)
    assert not os.path.exists(sql_path)

# ================================================================
#                       test pull fluege function
# ================================================================

def test_convertCSVToSQL():
    # check if already exists handling:
    sql_path = "example.sqlite"
    removeOldDBIfExists(sql_path,verbose = True, requires_confirmation=False)

    csv_path = "example.csv"
    url = "https://offenedaten-koeln.de/sites/default/files/Kompensationszahlungen_Fluege.csv"
    saveCSVLocally(csv_path,url)
    convertCSVToSQL(True, csv_path,sql_path)

    assert os.path.isfile(sql_path)

    # checking row count
    conn = sqlite3.connect(sql_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    # Execute a query to get the row count from the table "t"
    cursor.execute("SELECT COUNT(*) FROM t")
    row_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA table_info(t)")
    column_count = len(cursor.fetchall())

    # Close the cursor and the database connection
    cursor.close()
    conn.close()
    assert (row_count == 236)
    assert (column_count == 4)

    os.remove(csv_path)
    os.remove(sql_path)

