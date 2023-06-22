import json
import os.path
import sqlite3
from .utils import removeOldDBIfExists
import geopy.distance
from pyhafas import HafasClient
from pyhafas.profile import DBProfile
import datetime 
from datetime import timedelta
import time 

REGIONAL_EMISSIONS_TRAIN_VALUE = 93 # g/km
INTERREGIONAL_EMISSIONS_TRAIN_VALUE = 46 # g/km


# THIS DATA IS ALSO GENERATED AUTOMATICALLY. PLEASE READ COMMENTS
# this look ups has manually looked up flight times, train times and flagged if not direct 
# value[0] for flight duration in minutes for monday, 07/10/23 as seen on google flights
# value[1] for train duration in minutes for monday, 06/12/23 8am fetched from hafas client 
# value[2] flag set to 1 if flight was not direct, 0 for nonstop flights
# the lookups dict is supposed to be a permanent and easy fall back method and is thus in the source code and should not be modified
lookups ={
"CGN-TXL": [70,354,0],
"CGN-FRA": [180,64,1],# no direct
"CGN-MUC": [70,342,0],
"CGN-HAM": [65,316,0],
"MUC-CGN": [70,369,0],
"DUS-TXL": [70,318,0],
"MUC-TXL": [60,371,0],
"TXL-CGN": [70,433,0],
"CGN-DRS": [200,407,1],# no direct
"CGN-BER": [70,357,0],
"TXL-DUS": [70,392,0],
"DUS-DRS": [165,432,1],# no direct
"NUE-CGN": [270,232,1],# no direct
"CGN-LEJ": [195,422,1],# no direct
"LEJ-CGN": [195,309,1],# no direct
"DRS-CGN": [200,407,1],# no direct
"DUS-LEJ": [170,328,1],# no direct
}

# these values are manully looked up using the UmweltMobilCheck tool 
emissions_lookup = {
    "CGN-TXL" : [2200,15100],
    "CGN-MUC" : [2900,15600],
    "CGN-DRS" : [460,16400],
}

def calculate_aerial(coords):
    c = []
    for coord in coords:
        coord = coord.replace(",",".")
        c.append(float(coord))
    # coords = [origin_lat,origin_long,dest_lat,dest_long]
    # (lat, long) = (breite, laenge)
    return int(geopy.distance.geodesic((c[0],c[1]) , (c[2],c[3])).km)
            
def estimate_duration(aerial):
    return int((aerial / 800) * 60 + 30)


def lookup_flight_duration(trip, flight_duration_estimated):
    if trip not in lookups:
        print(trip + " was not found. using estimated duration")
        return flight_duration_estimated
    else:
        return lookups[trip][0]

def get_train_duration(trip, trip_train_info, use_lookup = True):
    if use_lookup:
        if trip in lookups:
            duration = lookups[trip][1]
            return duration
        else: 
            print("manually fetching for trip " + trip + " from json")
    return int (trip_train_info[trip].duration / 60)

def is_regional(name):
    # assuming regional if name is None
    if name is None:
        return True
    
    # interregional if name contains IC
    if "IC" in name:
        return False
    return True

def get_train_info(client, cur, trip, train_origin, train_destination, trip_train_info):
    if trip in trip_train_info:
        return
    
    # Get the current date and time
    current_date = datetime.datetime.now()

    # Find the previous Monday
    delta_days = (current_date.weekday() - 0) % 7  # 0 represents Monday
    previous_monday = current_date - timedelta(days=delta_days)

    # Set the time to 8 AM
    monday_8am = datetime.datetime.combine(previous_monday.date(), datetime.time(8, 0)) 
   
    train_info = client.journeys(
            destination=train_destination,
            origin=train_origin,
            date=monday_8am,
            min_change_time=0,
            max_changes=-1,
            max_journeys=1
        )[0]
    journey_info = {}
    journey_info["duration_min"] = int(train_info.duration.total_seconds()/60)

    regional_legs = []
    interregional_legs = []
    leg_station_names = []

    #stations might be double as stops include start and end stop as well but have to be included in case there is one leg regional and then one interregional
    for leg in train_info.legs:
        leg_station_names.append(leg.origin.name)
        
        r = []
        r.append(leg.origin.id)
        # store in regional stations
        if leg.stopovers is not None:
            for stopover in leg.stopovers[1:]:
                r.append(stopover.stop.id)

        # store in interregional stations
        if not is_regional(leg.name): 
            interregional_legs.append(r)
        # store in regional stations
        if is_regional(leg.name): 
            regional_legs.append(r)


    reg_coords = []
    interreg_coords = []
    # could have used long and lat from hafas but decided to stay with this solution
    for leg in regional_legs:
        r = []
        for station in leg:
            cur.execute('SELECT lat,long,lat FROM t WHERE evanr = ?', (station,))
            result = cur.fetchone()
            lat = float(result[0].replace(",","."))
            long = float(result[1].replace(",","."))
            r.append([lat,long])
        reg_coords.append(r)

    for leg in interregional_legs:
        r = []
        for station in leg:
            cur.execute('SELECT lat,long,lat FROM t WHERE evanr = ?', (station,))
            result = cur.fetchone()
            lat = float(result[0].replace(",","."))
            long = float(result[1].replace(",","."))
            r.append([lat,long])
        interreg_coords.append(r)

    journey_info["regional_legs"] = regional_legs
    journey_info["interregional_legs"] = interregional_legs
    journey_info["leg_station_names"] = leg_station_names
    journey_info["reg_coords"] = reg_coords
    journey_info["interreg_coords"] = interreg_coords

    trip_train_info[trip] = journey_info
    time.sleep(0.2)

def get_distance_from_coord_list(coords):
    total_distance = 0
    for i in range(len(coords)-1):
        o = coords[i]     
        d = coords[i+1]
        distance= int(geopy.distance.geodesic((o[0],o[1]) , (d[0],d[1])).km) 
        total_distance += distance
    return total_distance


def get_train_distance(trip, trip_train_info):
    if trip not in trip_train_info:
        raise ValueError("trip not found")
    if "total_distance" in trip_train_info[trip]:
        return trip_train_info[trip]["total_distance"]
    regional_distance = 0
    for leg in trip_train_info[trip]["reg_coords"]:
        regional_distance += get_distance_from_coord_list(leg)
    interregional_distance = 0
    for leg in trip_train_info[trip]["interreg_coords"]:
        interregional_distance += get_distance_from_coord_list(leg)


    trip_train_info[trip]["reg_distance"] = regional_distance
    trip_train_info[trip]["interreg_distance"] = interregional_distance
    total_distance = regional_distance + interregional_distance
    trip_train_info[trip]["total_distance"] = total_distance

    return total_distance

def get_only_regional_emissions(trip,trip_train_info):
    if trip not in trip_train_info:
        raise ValueError("trip not found")
    if "reg_distance" not in trip_train_info[trip]:
        raise ValueError("no reg_distance not found")
    regional_distance = trip_train_info[trip]["reg_distance"]
    regional_emissions_in_g = int(regional_distance * REGIONAL_EMISSIONS_TRAIN_VALUE)

    return regional_emissions_in_g


def get_both_emissions(trip,trip_train_info):
    if trip not in trip_train_info:
        raise ValueError("trip not found")
    if "total_distance" not in trip_train_info[trip]:
        raise ValueError("no reg_distance not found")
    regional_distance = trip_train_info[trip]["reg_distance"]
    interregional_distance = trip_train_info[trip]["interreg_distance"]
    regional_emissions_in_g = int(regional_distance * REGIONAL_EMISSIONS_TRAIN_VALUE)
    interregional_emissions_in_g = int(interregional_distance * INTERREGIONAL_EMISSIONS_TRAIN_VALUE)

    total_emissions_in_g = regional_emissions_in_g + interregional_emissions_in_g
    return total_emissions_in_g


def createFlightComparison(verbose, flights_comp, flight_duration_comparison_sql_file):
    removeOldDBIfExists(flight_duration_comparison_sql_file,verbose, requires_confirmation=False)

    con = sqlite3.connect(flight_duration_comparison_sql_file)
    cur = con.cursor()
    query = f"CREATE TABLE t (trip, estimated_duration, actual_duration, nonstop)"
    con.execute(query)
    to_db = []
    for key, v in flights_comp.items():
        to_db.append([key,v[0],v[1],v[2]])
    cur.executemany("INSERT INTO t (trip, estimated_duration, actual_duration, nonstop) VALUES (?, ?, ?, ?);", to_db)
    con.commit()    
    if verbose:
        print("created new database 'flight_comp.sqlite' with " + str(len(to_db)) + " entries.")
    #close connection
    con.close()

def createCountedTripEmissions(verbose, emission_trip_counter, counted_trip_emissions_sql_file):
    removeOldDBIfExists(counted_trip_emissions_sql_file,verbose, requires_confirmation=False)

    con = sqlite3.connect(counted_trip_emissions_sql_file)
    cur = con.cursor()
    query = f"CREATE TABLE t  (trip, count, train_emission_A_own, market_based_UMC, train_emission_B_own, location_based_UMC)"
    con.execute(query)
    to_db = []

    # sort them by most occuring trip
    sorted_em = {k: v for k, v in sorted(emission_trip_counter.items(), key=lambda item: item[1][0], reverse=True)}
    

    for key, v in sorted_em.items():
        index = v[0]
        a_own = v[1]
        a_UMC = v[2]
        b_own = v[3]
        b_UMC = v[4]
        if key in emissions_lookup:
            a_UMC = emissions_lookup[key][0]
            b_UMC = emissions_lookup[key][1]

        to_db.append([key,index, a_own, a_UMC, b_own, b_UMC])
    cur.executemany("INSERT INTO t (trip, count, train_emission_A_own, market_based_UMC, train_emission_B_own, location_based_UMC) VALUES (?, ?, ?, ?, ?, ?);", to_db)
    con.commit()    
    if verbose:
        print("created new database 'counted_trip_emissions.sqlite' with " + str(len(to_db)) + " entries.")
    #close connection
    con.close()    


def _addDistancesAndDurations(verbose,use_real_durations, domestic_flights_sql_file, train_stations_sql_file, domestic_distanced_flights_sql_file,flight_duration_comparison_sql_file,counted_trip_emissions_sql_file, trip_train_info_json):
    if not os.path.exists(domestic_flights_sql_file):
        if verbose:
            print("domestic_flights.sqlite does not exist. please run create_domestic_flights.py first")
        return
    if not os.path.exists(trip_train_info_json):
        if verbose:
            print("trip_train_info_json does not exist. creating new dictionary")
        trip_train_info = {}
    else:
        with open(trip_train_info_json, 'r', encoding="utf-8") as file:
            # Load the JSON data into a dictionary
            trip_train_info = json.load(file)
    
    # connect to domestic flights sql db 
    con = sqlite3.connect(domestic_flights_sql_file)
    cur = con.cursor()
    query = f"SELECT origin, origin_long, origin_lat, destination, dest_long, dest_lat, train_origin, train_dest, quantity, emissions FROM t"

    # Execute the query and storing the result 
    cur.execute(query)
    result = cur.fetchall()
    #close connection
    con.close()

    # get stats for report
    flights_comp = {}
    emission_trip_counter = {}

    # insert result in new database
    if result is not None:
        to_db = []
        client = HafasClient(DBProfile(), debug=True)

        # connect to trains_stations sql to look up coordinates on legs
        con = sqlite3.connect(train_stations_sql_file)
        cur = con.cursor()

        # create dict entries adding the station origins and destinations
        for r in result:

            # provided data
            origin = r[0]
            origin_long = r[1]
            origin_lat = r[2]
            destination = r[3]
            dest_long = r[4]
            dest_lat = r[5]
            train_origin = r[6]
            train_dest = r[7]
            quantity =int(r[8])
            flight_emissions = int(r[9])*1000

            trip = origin+"-"+destination
            # additional required data
            aerial_distance= calculate_aerial([origin_lat,origin_long,dest_lat,dest_long])
            flight_duration= estimate_duration(aerial_distance)          

            actual_flight_duration = lookup_flight_duration(trip, flight_duration)

            # add flight durations to comparison
            if trip not in flights_comp:
                nonstop = "yes" if lookups[trip][2]==0 else "no"
                flights_comp[trip] = [flight_duration,actual_flight_duration, nonstop]

            # if flag is set use the actual duration for the database
            if use_real_durations:
                flight_duration= actual_flight_duration

            # getting the train info into trip_train_info 
            get_train_info(client, cur, trip, train_origin, train_dest, trip_train_info)

            # saves train distances in trip_train_info
            get_train_distance(trip, trip_train_info)

            train_duration= get_train_duration(trip, trip_train_info, use_lookup=True)
            train_emissions_A= get_only_regional_emissions(trip,trip_train_info)
            train_emissions_B= get_both_emissions(trip, trip_train_info)

            if trip not in emission_trip_counter:
                # unknown values for the UMC values. will be looked up later
                emission_trip_counter[trip] = [1,train_emissions_A,0,train_emissions_B,0]
            else:
                # increment count
                emission_trip_counter[trip][0] += 1

            to_db.append([origin, destination, flight_duration, train_duration, train_emissions_A, train_emissions_B, flight_emissions,quantity])

        con.close()
        # connect to new distancedflights sql db 
        con = sqlite3.connect(domestic_distanced_flights_sql_file)
        cur = con.cursor()
        query = f"CREATE TABLE t (origin, destination, flight_duration, train_duration, train_emissions_A, train_emissions_B, flight_emissions, quantity)"
        con.execute(query)

        cur.executemany("INSERT INTO t (origin, destination, flight_duration, train_duration, train_emissions_A, train_emissions_B, flight_emissions, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
        con.commit()    
        if verbose:
            print("created new database 'final.sqlite' with " + str(len(to_db)) + " entries.")


    else: 
        if verbose:
            print("could not find any flights in the domestic_flights_db")
    #close connection
    con.close()

    # now write files

    # creating flight duration comparison
    createFlightComparison(verbose,flights_comp, flight_duration_comparison_sql_file)    

    # create trip emission information
    createCountedTripEmissions(verbose, emission_trip_counter, counted_trip_emissions_sql_file)

    # Open the JSON file in write mode
    with open(trip_train_info_json, 'w', encoding="utf-8") as file:
        # Write the new data into the file, overwriting existing content
        json.dump(trip_train_info, file, ensure_ascii=False)


def addDistancesAndDurations(verbose, use_real_durations):
    # this is a json file to save the train infos to not overload api. When being deleted or cleared, its contents are newly fetched.
    # the lookups dict is supposed to be a permanent and easy fall back method that is supposed to be permanend and is thus in the source code and should not be modified
    trip_train_info_json = "data/trip_train_info.json"
    train_stations_sql_file = "data/train_stations.sqlite"
    domestic_flights_sql_file = "data/domestic_flights.sqlite"
    flight_duration_comparison_sql_file = "data/flight_comp.sqlite"
    domestic_distanced_flights_sql_file = "data/final.sqlite"
    counted_trip_emissions_sql_file = "data/counted_trip_emissions.sqlite"
    removeOldDBIfExists(domestic_distanced_flights_sql_file,verbose, requires_confirmation=False)

    delay = 1 
    while delay < 65:
        try:
            _addDistancesAndDurations(verbose, use_real_durations, domestic_flights_sql_file,train_stations_sql_file, domestic_distanced_flights_sql_file,flight_duration_comparison_sql_file,counted_trip_emissions_sql_file, trip_train_info_json)
            break
        except:
            delay *= 2
            removeOldDBIfExists(domestic_distanced_flights_sql_file,verbose, requires_confirmation=False)

            if verbose:
                print(f"did not work. try again in {delay} seconds...")
            time.sleep(delay)


