import datetime
# from pyhafas import HafasClient
# from pyhafas.profile import DBProfile
import json 
import sqlite3
# client = HafasClient(DBProfile(), debug=True)

# print(client.journeys(
#         destination="8001844",
#         origin="8001845",
#         date=datetime.datetime.now(),
#         min_change_time=0,
#         max_changes=-1,
#         max_journeys=1
#     )[0].duration)

def get_domestic_flights():
    domestic_flights_sql_file = "data/domestic_flights.sqlite"
    # connect to flights database
    con = sqlite3.connect(domestic_flights_sql_file)
    cur = con.cursor()

    query = f"SELECT origin,destination,quantity,emissions FROM t"

    cur.execute(query)
    result = cur.fetchall()
    return result

result = get_domestic_flights()
for row in result:
    print(row)

