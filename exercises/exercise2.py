import pandas
import csv
import sqlite3
import os
import re

url = "https://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV"
sql_path = 'exercises/trainstops.sqlite'

data = pandas.read_csv(url, delimiter=";")

# remove if already exists
if os.path.isfile(sql_path):
    os.remove(sql_path)

# Establish a connection to the SQLite database
conn = sqlite3.connect(sql_path)
cursor = conn.cursor()

# Create a table in the SQLite database
cursor.execute('''
    CREATE TABLE trainstops (
        Verkehr TEXT,
        Laenge REAL,
        Breite REAL,
        IFOPT TEXT
    )
''')

# Iterate over the rows of the DataFrame
for index, row in data.iterrows():
    # Extract the values from the row
    verkehr = row['Verkehr']
    laenge = row['Laenge']
    breite = row['Breite']
    ifopt = str(row['IFOPT'])

    # Check if the value in 'Verkehr' matches the regex pattern
    if not re.search(r"RV|nur DPN|FV", verkehr):
        print("found invalid verkehr data: " + str(verkehr))
        continue  # Skip this iteration and move to the next row

    # Check if laenge and breite are floats between -90 and 90
    try:
        breite_float = float(breite.replace(',', '.'))
        laenge_float = float(laenge.replace(',', '.'))
        if not (-90 <= laenge_float <= 90):
            print("Variable breite is a float between -90 and 90.")
            continue    
        if not(-90 <= breite_float <= 90):
            print("Variable laenge is not within the range of -90 to 90.")
    except ValueError:
        print("Variable cannot be converted to a float.")
        continue

    # check if ifopt matches pattern
    pattern = r"[A-Za-z][A-Za-z][0-9]*:[0-9]*(:[0-9]*)?"
    if not re.search(pattern, ifopt):
        print("found invalid ifopt: " + str(ifopt))
        continue  # Skip this iteration and move to the next row




    # Insert the values into the SQLite table
    cursor.execute('''
        INSERT INTO trainstops (Verkehr, Laenge, Breite, IFOPT)
        VALUES (?, ?, ? , ?)
    ''', (verkehr, laenge_float, breite_float, ifopt))

# Commit the changes and close the connection
conn.commit()
conn.close()

