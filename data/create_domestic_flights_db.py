import json
import os.path
import sqlite3

flights_sql_file = "data/fluege.sqlite"
domestic_flights_sql_file = "data/domestic_flights.sqlite"
mapped_airports_file = "data/mapped_airports.json"

def createDomesticFlightsDB():

    if not os.path.exists(flights_sql_file):
        print("fluege sqlite does not exist. please run pull_fluege_db.py first")
        return
    if os.path.exists(domestic_flights_sql_file):

        confirmation = input("Are you sure you want to delete the old database domestic_flights.sqlite? (no backup will be made) \n(y/n): ")
        if confirmation.lower() == "y":
            os.remove(domestic_flights_sql_file)
            print("old database deleted successfully.")
        else:
            print("Deletion cancelled. Not creating new database")
            return
    else:
        print("Database does not exist. Creating new one...")

    # connect to flights database
    con = sqlite3.connect(flights_sql_file)
    cur = con.cursor()

    # load mapped airports json
    with open(mapped_airports_file, "r",encoding="utf-8") as fin: 
        mapped_airports = json.load(fin)

    # create query string querying all domestic airports (there might a more efficient solution)
    dest_list = ""
    origin_list = ""
    for k,_ in mapped_airports["station-mapping"].items():
        dest_list += (f" OR destination LIKE '{k}'")
        origin_list += (f" OR origin LIKE '{k}'")
    dest_list = "(" + dest_list[4:] + ")"
    origin_list = "(" + origin_list[4:] + ")"

    #select only flights with both origin and destination are in mapped airports keys.
    query = f"SELECT origin,destination,quantity,emissions FROM t WHERE ({origin_list} AND {dest_list})"

    # Execute the query and storing the result 
    cur.execute(query)
    result = cur.fetchall()

    #closing old db connection
    con.commit()
    con.close()

    # opening new database
    con = sqlite3.connect(domestic_flights_sql_file)
    cur = con.cursor()
    cur.execute("CREATE TABLE t (origin, destination, train_origin, train_dest, quantity, emissions);") 

    # insert result in new database
    if result is not None:
        to_db = []

        # create dict entries adding the station origins and destinations
        for r in result:
            to_db.append((r[0],r[1],mapped_airports["station-mapping"][r[0]], mapped_airports["station-mapping"][r[1]],r[2],r[3]))

        cur.executemany("INSERT INTO t (origin, destination, train_origin, train_dest, quantity, emissions) VALUES (?, ?, ?, ?, ?, ?);", to_db)
        con.commit()    
        print("created new database with " + str(len(to_db)) + " entries.")
    else: 
        print("could not find any domestic flights in the database")

    #close connection
    con.close()


createDomesticFlightsDB()