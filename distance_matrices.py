global dffinald
global k
import json5
import urllib
import pandas
import os
from shapely.geometry import Polygon
import numpy
import sys
import getopt
import random
import string


def create_depot(input_file_name, input_polygon_name, input_stops):
    pol = pandas.read_csv(input_polygon_name)
    coordinates = pandas.read_csv(input_file_name)
    coord = []
    for i in range(len(coordinates)):
        coord.append([coordinates.latitud[i], coordinates.longitud[i], coordinates.Frequency[i]])
    d = []
    for i in range(len(pol.latitud)):
        d.append((pol.latitud[i], pol.longitud[
            i]))  # Saves the lat and long coordinates that will be used in order to create the polygon
    borders = Polygon(d)  # Creates the polygon
    bor = borders.bounds
    depot = [bor[2], bor[1], 0]
    coord = numpy.insert(coord, 0, depot, axis=0)
    # TODO Why write to disk?
    pandas.DataFrame(coord).to_csv(input_stops, index=False, header=['latitud', 'longitud', 'Frequency'])


apis = {'0': 'AIzaSyB0yjopeeI0St0ERZCMXZadpYv_MkEbDJQ', '1': 'AIzaSyDk09yuau5l3tdmZ0-NYxtu7u4Kv1aBqGw',
        '2': 'AIzaSyCRhnSh0H_GG9npR1O-9atpwLWgUIEOMtg', '3': 'AIzaSyDWblNWpIybgGmkkpt4_TQiMxhTlcgo8MM',
        '4': 'AIzaSyAGOBYE37X1Uy8RPqJuZaEb6w0W2DyaMW0', '5': 'AIzaSyDwQmDpHEDDlrJvLzUmdzZ_HZljRwJHDHM',
        '6': 'AIzaSyAC_U7yoBQgXtcb4Vb3_BjMfHaokuba-CY', '7': 'AIzaSyDJcv9bSoaNX9V2R1cWAiNsyklCsg3PgF8',
        '8': 'AIzaSyBd2ykfsGeJSSJL4rRQa-4HefpKYJOme5o', '9': 'AIzaSyC82GFlznnpc988o0WNf7xYFaXZexo4V-A',
        '10': 'AIzaSyCZz8sSJL0NeHmfE6wUgRKVEJymhZ3W-tM'}


def process(file_name, input, clients, output, distance_stops_to_stops, time_stops_to_stops,
            distance_stops_to_customers, time_stops_to_customer):
    k = 1
    mode = {'0': 'driving', '1': 'walking'}

    for itera in range(2):
        # Rename columns names in order to make them latitud and longitud
        if itera == 0:
            dataframe = pandas.read_csv(file_name)
            sub = dataframe[['latitud', 'longitud']]
            dataframe2 = pandas.read_csv(file_name)
            sub2 = dataframe2[['latitud', 'longitud']]
        else:
            dataframe = pandas.read_csv(file_name)
            dataframe = dataframe[dataframe.index > 0]
            dataframe = dataframe.reset_index()
            sub = dataframe[['latitud', 'longitud']]
            dataframe2 = pandas.read_csv(clients)
            sub2 = dataframe2[['latitud', 'longitud']]
        dffinald = []
        dffinalt = []
        l = 0
        p = 0
        for i in range(len(sub.latitud)):
            dffinald.append([])
            dffinalt.append([])
            # Agrega una fila
            for j in range(len(sub2.latitud)):

                orig_coord = (sub.latitud[i], sub.longitud[i])
                dest_coord = (sub2.latitud[j], sub2.longitud[j])
                try:
                    #                url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode='+str(mode[str(itera)])+'&sensor=false&key={2}'.format(str(orig_coord),str(dest_coord),str(apis[str(k)]))
                    #                url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode={2}&sensor=false&key={3}'.format(str(orig_coord),str(dest_coord),+str(mode[str(itera)]),str(apis[str(k)]))
                    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode={2}&sensor=false&key={3}'.format(
                        str(orig_coord), str(dest_coord), str(mode[str(itera)]), str(apis[str(k)]))
                    result = json5.load(urllib.urlopen(url))
                    #print result
                    tript = result['rows'][0]['elements'][0]['duration']['value']
                    tripd = result['rows'][0]['elements'][0]['distance']['value']
                    dffinald[i].append(tripd)
                    dffinalt[i].append(tript)
                    #print (i, j, 'ok', k)

                except AttributeError:
                    k = k + 1
                    #print (i, j, 'AE', k)
                    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode={2}&sensor=false&key={3}'.format(
                        str(orig_coord), str(dest_coord), str(mode[str(itera)]), str(apis[str(k)]))
                    result = json5.load(urllib._urlopener(url))
                    tript = result['rows'][0]['elements'][0]['duration']['value']
                    tripd = result['rows'][0]['elements'][0]['distance']['value']
                    dffinald[i].append(tripd)
                    dffinalt[i].append(tript)
                    #print result
                except IOError:
                    #print (i, j, 'IO', k)
                    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode={2}&sensor=false&key={3}'.format(
                        str(orig_coord), str(dest_coord), str(mode[str(itera)]), str(apis[str(k)]))
                    result = json5.load(urllib._urlopener(url))
                    tript = result['rows'][0]['elements'][0]['duration']['value']
                    tripd = result['rows'][0]['elements'][0]['distance']['value']
                    dffinald[i].append(tripd)
                    dffinalt[i].append(tript)
                except IndexError:
                    #print (i, j, 'IE', k)
                    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode={2}&sensor=false&key={3}'.format(
                        str(orig_coord), str(dest_coord), str(mode[str(itera)]), str(apis[str(k)]))
                    result = json5.load(urllib._urlopener(url))
                    tript = result['rows'][0]['elements'][0]['duration']['value']
                    tripd = result['rows'][0]['elements'][0]['distance']['value']
                    dffinald[i].append(tripd)
                    dffinalt[i].append(tript)

                l = l + 1
                p = p + 1
                #print (i, j, l, p)
                if (l == 2400):
                    l = 0
                    k = k + 1
        if itera == 0:
            pandas.DataFrame(dffinald).to_csv(distance_stops_to_stops, index=False, header=None)
            pandas.DataFrame(dffinalt).to_csv(time_stops_to_stops, index=False, header=None)
        else:
            pandas.DataFrame(dffinald).to_csv(distance_stops_to_customers, index=False, header=None)
            pandas.DataFrame(dffinalt).to_csv(time_stops_to_customer, index=False, header=None)


def main(argv):
    input = "input.csv"
    output = "output.csv"
    polygon_file_name = "polygon.csv"
    client_file_name = "clients.csv"
    distance_stops_to_stops = "distance_stops_to_stops.csv"
    time_stops_to_stops = "time_stops_to_stops.csv"
    distance_stops_to_customers = "distance_stops_to_customers.csv"
    time_stops_to_customer = "time_stops_to_customer.csv"

    hash_name = ''.join(random.choice(string.ascii_uppercase) for i in range(24))
    hash_name += ".csv"

    try:
        opts, args = getopt.getopt(argv, "i:o:p:t:v:x:y:z:",
                                   ["input=", "output=", "polygon=", "clients=", "distance_stops_to_stops=",
                                    "time_stops_to_stops=", "distance_stops_to_customers", "time_stops_to_customers="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-p", "--polygon"):
            polygon_file_name = arg
        elif opt in ("-t", "--clients"):
            client_file_name = arg
        elif opt in ("-v", "--distance_stops_to_stops"):
            distance_stops_to_stops = arg
        elif opt in ("-x", "--time_stops_to_stops"):
            time_stops_to_stops = arg
        elif opt in ("-y", "--distance_stops_to_customers"):
            distance_stops_to_customers = arg
        elif opt in ("-z", "--time_stops_to_customers"):
            time_stops_to_customer = arg

    create_depot(input, polygon_file_name, hash_name)

    process(hash_name, input, client_file_name, output, distance_stops_to_stops, time_stops_to_stops, distance_stops_to_customers, time_stops_to_customer)

    os.remove(hash_name)

if __name__ == "__main__":
    main(sys.argv[1:])
