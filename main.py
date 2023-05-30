from data.pull_fluege_db import pull_fluege_db
from data.pull_train_stations_db import pull_train_stations
from data.create_LUT import createTable
from data.create_domestic_flights_db import createDomesticFlightsDB

def pipeline():
    # creating fluege database from datasource
    pull_fluege_db()

    # creating train station database from second data source
    pull_train_stations()

    # creating look up table from used airports and corresponding cities
    createTable()

    # create final table that maps flights and origin and destination to the flight entries
    createDomesticFlightsDB()

if __name__ == "__main__":
    pipeline()
