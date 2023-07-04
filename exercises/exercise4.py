import pandas
import sqlite3
import os
import re
import urllib.request
from zipfile import ZipFile
import shutil 

url = "https://www.mowesta.com/data/measure/mowesta-dataset-20221107.zip"
sql_path = 'temperatures.sqlite'


zip = urllib.request.urlretrieve(url,"ex4_data.zip")


with ZipFile('ex4_data.zip', 'r') as f:
    #extract in current directory
    f.extractall("ex4_data")

csv_path = os.path.join(os.getcwd(),"ex4_data","data.csv")
data = pandas.read_csv(csv_path, sep=";", usecols=[0,1,2,3,4,9,10], header=None)

shutil.rmtree("ex4_data")
os.remove("ex4_data.zip")

data= data.tail(-1) # drop first row
print(data.head())

# remove if already exists
if os.path.isfile(sql_path):
    os.remove(sql_path)

# Establish a connection to the SQLite database
conn = sqlite3.connect(sql_path)
cursor = conn.cursor()

# Create a table in the SQLite database
cursor.execute('''
    CREATE TABLE temperatures (
        Geraet INT,
        Hersteller TEXT,        
        Model TEXT,
        Monat INT,
        Temperatur FLOAT,
        Batterietemperatur FLOAT,
        "Geraet aktiv" TEXT
    )
''')

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
    g = int(row[0])
    h = row[1]
    m = row[2]
    mo = int(row[3])
    t = float(row[4].replace(',', '.'))
    bt = float(row[9].replace(',', '.'))
    ga = row[10]

    t = (t*9/5) + 32
    bt = (bt*9/5) + 32

    # # Check if the value in 'Verkehr' matches the regex pattern
    # if verkehr != "RV":
    #     if verkehr != "nur DPN":
    #         if verkehr != "FV":
    #             print("found invalid verkehr data: " + str(verkehr))
    #             continue  # Skip this iteration and move to the next row


    # # Check if laenge and breite are floats between -90 and 90
    # try:
    #     breite_float = float(breite.replace(',', '.'))
    #     laenge_float = float(laenge.replace(',', '.'))
    #     if not (-90 <= laenge_float <= 90):
    #         print("Variable breite is a float between -90 and 90.")
    #         continue    
    #     if not(-90 <= breite_float <= 90):
    #         print("Variable laenge is not within the range of -90 to 90.")
    # except ValueError:
    #     print("Variable cannot be converted to a float.")
    #     continue

    # # check if ifopt matches pattern
    # pattern = r"[A-Za-z][A-Za-z]:[0-9]*:[0-9]*(:[0-9]*)?"
    # if not re.search(pattern, ifopt):
    #     print("found invalid ifopt: " + str(ifopt))
    #     continue  # Skip this iteration and move to the next row




    # Insert the values into the SQLite table
    cursor.execute('''
        INSERT INTO temperatures (Geraet,Hersteller, Model,Monat, Temperatur, Batterietemperatur,"Geraet aktiv") VALUES (?,?,?, ?, ? ,?, ?)
    ''', (g,h,m,mo,t, bt, ga))

# Commit the changes and close the connection
conn.commit()
conn.close()

