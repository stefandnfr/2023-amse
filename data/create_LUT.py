# this creates a look up table from all the used airports and its corresponding cities
# dependencies: 
#   -fluege.sqlite and train_stations.sqlite (needs those dbs to find look up matches)
#   -german-airports.csv (hardcoded csv that contains german airports that were flown in 2019 from fluege.sqlite)
#creates: - mapped_airports.json (a mapping between airport codes and corresponding train stations)

import sqlite3
import os
import csv 
import json 


def createTable():
    flights_sql_file  = "data/fluege.sqlite"
    stations_sql_file  = "data/train_stations.sqlite"
    csv_file = "data/german-airports.csv"
    mapped_airports_file = "data/mapped_airports.json"


    if not os.path.exists(flights_sql_file):
        print("fluege.sqlite does not exist. Can not create look up table if flight origins and destinations are not known. Try to run pull_fluege_db.py first")
        return
    con = sqlite3.connect(flights_sql_file)
    cur = con.cursor()
    # Execute a query to get distinct values from two columns
    cur.execute("SELECT DISTINCT value FROM (SELECT origin AS value FROM t UNION SELECT destination AS value FROM t) ORDER BY value;")

    # Fetch all the results as a list
    results = cur.fetchall()



    # this csv file was generated from wikipedia as airports in Germany usually do not fluctuate too much
    with open(csv_file, "r", encoding="utf-8") as fin: 
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin,delimiter=";") # comma is default delimiter
        german_airports = dict([(i["iata"], i["location"]) for i in dr])
    
    mapped_airports = {}

    # Add the needed airport codes to mapped airports
    for row in results:
        iata_code = row[0]
        if iata_code in german_airports:
            #add iata code in mapped list:
            mapped_airports[iata_code] = german_airports[iata_code]
        #else:
            #print(iata_code + " is not in german airport code list")

    data = {}
    data["city-mapping"] = mapped_airports

    #now mapping the cities to their train stations
    mapped_train_stations = {}
    if not os.path.exists(stations_sql_file):
        print("train_stations.sqlite does not exist. Can not create look up table if train stations are not known. Try to run pull_train_stations_db.py first")
        return
    con = sqlite3.connect(stations_sql_file)
    cur = con.cursor()

    for iata,city in mapped_airports.items():
        #print(city)
        search_name = city 
        #print("searching train station for " + search_name)
        query = f"SELECT evanr,name FROM t WHERE (name LIKE '%{search_name}%' OR name LIKE '%{iata}%') AND (name like '%Flughafen%' OR name like '%Airport%') LIMIT 1"
        # Execute the query
        cur.execute(query)
        # Fetch the result
        result = cur.fetchone()
        # Store the first column of the first row in a variable 
        if result is not None:

            #station name just for check if station name somewhat is close to airport
            #station_name = result[1]
            eva_nr = result[0]
            mapped_train_stations[iata] = eva_nr
            #print("Found: " + station_name + " with eva nr " + eva_nr +  " for airport " + iata)
        else:
            # Nuremberg has no train station only Ubahn
            if iata == "NUE":
                mapped_train_stations["NUE"] = "8000284"
            elif iata == "TXL":
                mapped_train_stations["TXL"] = "8089089"
            else:
                print("did not find " + iata)



    data["station-mapping"] = mapped_train_stations
    # Export dictionary as JSON
    with open(mapped_airports_file, 'w', encoding="utf-8") as f:
        json.dump(data, f,ensure_ascii=False)

