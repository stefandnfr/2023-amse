from data.pull_fluege_db import pull_fluege_db
from data.pull_train_stations_db import pull_train_stations
from data.create_LUT import createTable
from data.create_domestic_flights_db import createDomesticFlightsDB
from data.add_distances import addDistancesAndDurations

def pipeline(verbose):
    # creating fluege database from datasource
    pull_fluege_db(verbose)

    # creating train station database from second data source
    pull_train_stations(verbose)

    # creating look up table from used airports and corresponding cities
    createTable(verbose)

    # create working table that maps flights and origin and destination to the flight entries
    createDomesticFlightsDB(verbose)

    # add distances and durations to final table to be displayed in report
    addDistancesAndDurations(verbose)

if __name__ == "__main__":
    pipeline(verbose = True)
