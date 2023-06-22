from data.pull_fluege_db import pull_fluege_db
from data.pull_train_stations_db import pull_train_stations
from data.create_LUT import createTable
from data.create_domestic_flights_db import createDomesticFlightsDB
from data.add_distances import addDistancesAndDurations
import pandas as pd
import matplotlib.pyplot as plt

def pipeline(verbose, use_real_durations = False):
    # creating fluege database from datasource
    pull_fluege_db(verbose)

    # creating train station database from second data source
    pull_train_stations(verbose)

    # creating look up table from used airports and corresponding cities
    createTable(verbose)

    # create working table that maps flights and origin and destination to the flight entries
    createDomesticFlightsDB(verbose)

    # add distances and durations to final table to be displayed in report
    addDistancesAndDurations(verbose, use_real_durations)

def showFirstRow():
    df = pd.read_sql_table('t', 'sqlite:///data/final.sqlite')
    return df.head(1)

def showFlightComparison(length):
    if length > 17:
        print("Can only display the total 17 rows")
    df = pd.read_sql_table('t', 'sqlite:///data/flight_comp.sqlite')
    return df.head(length)    

def showEmissionComparison():
    df = pd.read_sql_table('t', 'sqlite:///data/counted_trip_emissions.sqlite')
    return df.head(3)    


def showTime():

    # Values for the bar chart
    time_flight = 12
    time_train = 10

    # Data for the x-axis and y-axis
    x = ['Flight', 'Train']
    y = [time_flight, time_train]

    # Create the bar chart
    plt.bar(x, y)

    # Add labels and title
    plt.xlabel('Method of Transportation')
    plt.ylabel('Time (minutes)')
    plt.title('Total Travel Time Comparison')

    # Display the chart
    return plt.show()

def showEmissions():
    return None

if __name__ == "__main__":
    pipeline(verbose = True, use_real_durations= False)
