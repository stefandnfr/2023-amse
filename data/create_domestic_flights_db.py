import json
import os.path
import sqlite3
from .utils import removeOldDBIfExists

def createSQL(verbose,flights_sql_file, domestic_flights_sql_file, mapped_airports_file):
    if not os.path.exists(flights_sql_file):
        if verbose:
            print("fluege sqlite does not exist. please run pull_fluege_db.py first")
        return
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
    cur.execute("CREATE TABLE t (origin, origin_long, origin_lat, destination, dest_long, dest_lat, train_origin, train_dest, quantity, emissions);") 

    # insert result in new database
    if result is not None:
        to_db = []

        # create dict entries adding the station origins and destinations
        for r in result:
            origin = r[0]
            destination = r[1]
            train_origin = mapped_airports["station-mapping"][origin]["eva_nr"]
            origin_long = mapped_airports["station-mapping"][origin]["long"]
            origin_lat = mapped_airports["station-mapping"][origin]["lat"]
            dest_long = mapped_airports["station-mapping"][destination]["long"]
            dest_lat = mapped_airports["station-mapping"][destination]["lat"]
            train_dest = mapped_airports["station-mapping"][destination]["eva_nr"]
            quantity = r[2]
            emissions = r[3]
            to_db.append([origin, origin_long, origin_lat, destination, dest_long, dest_lat, train_origin, train_dest, quantity, emissions])

        cur.executemany("INSERT INTO t (origin, origin_long, origin_lat, destination, dest_long, dest_lat, train_origin, train_dest, quantity, emissions) VALUES (?,?,?,?,?, ?, ?, ?, ?, ?);", to_db)
        con.commit()  
        if verbose:
            print("created new database with " + str(len(to_db)) + " entries.")
    else: 
        if verbose:
            print("could not find any domestic flights in the database")

    #close connection
    con.close()


def createDomesticFlightsDB(verbose):
    flights_sql_file = "data/fluege.sqlite"
    domestic_flights_sql_file = "data/domestic_flights.sqlite"
    mapped_airports_file = "data/mapped_airports.json"
    removeOldDBIfExists(domestic_flights_sql_file,verbose, requires_confirmation=False)
    createSQL(verbose, flights_sql_file, domestic_flights_sql_file, mapped_airports_file)

