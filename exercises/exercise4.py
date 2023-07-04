import pandas
import sqlite3
import os
import urllib.request
from zipfile import ZipFile
import shutil 

url = "https://www.mowesta.com/data/measure/mowesta-dataset-20221107.zip"
sql_path = 'temperatures.sqlite'

# get and unpack zip
zip = urllib.request.urlretrieve(url,"ex4_data.zip")
with ZipFile('ex4_data.zip', 'r') as f:
    f.extractall("ex4_data")

csv_path = os.path.join(os.getcwd(),"ex4_data","data.csv")

# only import certain columns as some rows are variable length
data = pandas.read_csv(csv_path, sep=";", usecols=[0,1,2,3,4,9,10], header=None)

# remove artifacts
shutil.rmtree("ex4_data")
os.remove("ex4_data.zip")

# drop first row which was header
data= data.tail(-1) 

# remove sql if already exists
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

# drop NANs
data = data.dropna(axis=0)

print("Found " + str(len(data)) + " non empty rows")

# Iterate over the rows of the DataFrame
for index, row in data.iterrows():

    # Extract the values from the row
    g = int(row[0])
    h = row[1]
    m = row[2]
    mo = int(row[3])

    # extract temperatures as floats
    try:
        t = float(row[4].replace(',', '.'))
        bt = float(row[9].replace(',', '.'))
    except:
        print("temperatures cannot be converted to a float.")
        continue        
    ga = row[10]

    # convert to fahrenheit
    t = (t*9/5) + 32
    bt = (bt*9/5) + 32

    # # Check if the value in geraete id is greater than 0
    if g <= 0:
        print("found invalid Geraete id: " + str(g))
        continue  # Skip this iteration and move to the next row

    # Check if temperatures are floats between 0 and 130
    if t < 0.0 or t > 130.0:
        print("temperature to high: " + str(t))
        continue

    # Check if temperatures are floats between 0 and 130
    if bt < 0.0 or bt > 130.0:
        print("battery temperature to high: " + str(bt))
        continue

    # Insert the values into the SQLite table
    cursor.execute('''
        INSERT INTO temperatures (Geraet,Hersteller, Model,Monat, Temperatur, Batterietemperatur,"Geraet aktiv") VALUES (?,?,?, ?, ? ,?, ?)
    ''', (g,h,m,mo,t, bt, ga))

# Commit the changes and close the connection
conn.commit()
conn.close()

