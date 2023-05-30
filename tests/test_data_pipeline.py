from data.pull_fluege_db import saveCSVLocally,convertCSVToSQL,removeOldDBIfExists
import data.pull_fluege_db
import sqlite3
# from ..data.pull_fluege_db import saveCSVLocally

import os
def test_saveCSVlocally_checkIfExists():
    path = "example.csv"
    saveCSVLocally(path)
    assert os.path.isfile(path)
    os.remove(path)

def test_removeOldDBIfExists():
    # checking if exists when there is a sqlite file
    sql_path = "example.sqlite"
    removeOldDBIfExists(sql_path, requires_confirmation= False)
    assert not os.path.exists(sql_path)

    #now checking if there isnt one
    removeOldDBIfExists(sql_path,requires_confirmation=False)
    assert not os.path.exists(sql_path)

def test_convertCSVToSQL():
    # check if already exists handling:
    sql_path = "example.sqlite"
    removeOldDBIfExists(sql_path,requires_confirmation=False)

    csv_path = "example.csv"
    saveCSVLocally(csv_path)
    convertCSVToSQL(csv_path,sql_path)

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




#test_saveCSVlocally_checkIfExists()