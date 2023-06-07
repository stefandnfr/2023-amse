import pandas
import csv
import sqlite3
import os
import re

url = "https://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV"
sql_path = 'trainstops.sqlite'

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
        EVA_NR BIGINT,
        DS100 TEXT,        
        IFOPT TEXT,
        NAME TEXT,
        Verkehr TEXT,
        Laenge REAL,
        Breite REAL,
        Betreiber_Name TEXT,
        Betreiber_Nr INT
    )
''')
data = data.drop("Status",axis=1)
data = data.dropna(axis=0)

print("Found " + str(len(data)) + " non empty rows")

# Iterate over the rows of the DataFrame
for index, row in data.iterrows():

    # remove one data point as there is one invalid data point according to the test
    empty = False
    for r in row:
        if pandas.isnull(r):
            empty = True
    if empty:
        continue

    # Extract the values from the row
    eva_nr = row['EVA_NR']
    ds = row['DS100']
    name = row['NAME']
    verkehr = row['Verkehr']
    laenge = row['Laenge']
    breite = row['Breite']
    ifopt = str(row['IFOPT'])
    betreiber_name = row["Betreiber_Name"]
    betreiber_nr = row["Betreiber_Nr"]

    # Check if the value in 'Verkehr' matches the regex pattern
    if verkehr != "RV":
        if verkehr != "nur DPN":
            if verkehr != "FV":
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
    pattern = r"[A-Za-z][A-Za-z]:[0-9]*:[0-9]*(:[0-9]*)?"
    if not re.search(pattern, ifopt):
        print("found invalid ifopt: " + str(ifopt))
        continue  # Skip this iteration and move to the next row




    # Insert the values into the SQLite table
    cursor.execute('''
        INSERT INTO trainstops (EVA_NR,DS100,IFOPT,NAME,Verkehr,Laenge,Breite,Betreiber_Name,Betreiber_Nr)
        VALUES (?,?,?,?,?, ?, ? ,?, ?)
    ''', (eva_nr,ds,ifopt,name,verkehr, laenge_float, breite_float, betreiber_name,betreiber_nr))

# Commit the changes and close the connection
conn.commit()
conn.close()

