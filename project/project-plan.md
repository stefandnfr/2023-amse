# Project Plan

## Summary

This projects analyzes the business flights taken by the municipality of Cologne. It compares the CO2 emissions of the domestic flights taken in the year 2019 with public alternatives such as trains. The main focus will be given at duration of transport and estimated CO2 emission. 

## Rationale

The analysis helps municipalities and lawmakers to do reason about the necessity of domestic flights. It should show that there are equal alternatives and potential carbon emission reduction. 

## Datasources

### Datasource1: Dienstfluege CO2 Stadt Koeln 2019
* Metadata URL: https://mobilithek.info/offers/-1005216978664916194
* Data URL: https://offenedaten-koeln.de/sites/default/files/Kompensationszahlungen_Fluege.csv
* Data Type: CSV

Displays origin, destination, number of passengers and CO2 emission of 236 flights from the municipality of Cologne.

### Datasource2: Fahrplan Deutsche Bahn
* Metadata URL: https://www.govdata.de/ckan/dataset/fahrplan-api.rdf
* Data URL: https://developer.deutschebahn.com/store/apis/info?name=Fahrplan-Free&version=v1&provider=DBOpenData
* Data Type: API

Displays timetable of trains operated by Deutsche Bahn. 

## Work Packages

1. Integrate Datasource1 [#1][i1]
2. Get API Access [#2][i2]
3. Compare the durations of the flights and corresponding trains [#3][i3]
4. Compare the emissions of the flights and corresponding trains [#4][i4]
5. Visualize the data [#5][i5]


[i1]: https://github.com/stefandnfr/2023-amse/issues/1
[i2]: https://github.com/stefandnfr/2023-amse/issues/2
[i3]: https://github.com/stefandnfr/2023-amse/issues/3
[i4]: https://github.com/stefandnfr/2023-amse/issues/4
[i5]: https://github.com/stefandnfr/2023-amse/issues/5