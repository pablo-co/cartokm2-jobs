import os
from shapely.geometry import Point
from shapely.geometry import Polygon
import getopt
import sys
import random
import string
import pandas as pd  # pandas se utiliza para leer y escribir los archivos
from geopy.distance import vincenty  # las distancias entre los puntos son calculadas con esta libreria
from datetime import datetime  # esta libreria es utilizada para manejar las horas (sumar, restar y hacer comparaciones)
from datetime import \
    timedelta  # esta libreria es utilizada porque la suma o resta de fechas se convierte a este formato
import \
    numpy as np  # numpy crea matrices con una estructura diferente a pandas pero permite hacer queries especificos e iterar las matrices


def SecondFilter(input_file, polygon_file, hash_file, first_column_name, last_column_name, x):
    polsmall = pd.read_csv(polygon_file)  # Reads the polygon of the square kilometer

    d = []
    for i in range(len(polsmall.latitud)):
        d.append((polsmall.latitud[i], polsmall.longitud[
            i]))  # Saves the lat and long coordinates that will be used in order to create the polygon
    Km2 = Polygon(d)  # Creates the polygon

    data = pd.read_csv(input_file)

    filterbase = []
    for i in range(len(data)):
        q = Point((data.LATITUD[i], data.LONGITUD[i]))  # Obtains each point from the GPS traces
        TF = Km2.contains(q)  # Tests to see if the point is or not in the area that has been used for the study
        if TF == 1:
            filterbase.append(data.ix[i][first_column_name:"LONGITUD"])  # Saves each row
    filterbase = pd.DataFrame(filterbase)
    pd.DataFrame(filterbase).to_csv(hash_file, index=False)


def process(hash_file, fuel_input, capacity_input, co2, output, stats, traces, first_column_name, last_column_name, x):
    data = np.genfromtxt(hash_file, dtype=None,
                         delimiter=',')  # con esta instruccion se lee el archivo y se convierte en matriz numpy; al archivo se le quitaron las columnas de Direccion, Comuna y Patente y se agrego la columna Mes
    data2 = pd.read_csv(
        hash_file)  # al mismo tiempo se lee el archivo con pandas porque su formato es mas sencillo para realizar ciertas tareas

    a = first_column_name
    b = last_column_name
    tbt = x

    time = []
    time.append('HORA')
    time2 = []
    for i in range(len(data2)):
        time.append(str(int(data2.HORA[i] * 24)) + ':' + str(
            int(((data2.HORA[i] * 24) - int(data2.HORA[i] * 24)) * 60)) + ':' + str(int(((((data2.HORA[i] * 24) - int(
            data2.HORA[i] * 24)) * 60) - int(((data2.HORA[i] * 24) - int(data2.HORA[i] * 24)) * 60)) * 60)))
        time2.append(str(int(data2.HORA[i] * 24)) + ':' + str(
            int(((data2.HORA[i] * 24) - int(data2.HORA[i] * 24)) * 60)) + ':' + str(int(((((data2.HORA[i] * 24) - int(
            data2.HORA[i] * 24)) * 60) - int(((data2.HORA[i] * 24) - int(data2.HORA[i] * 24)) * 60)) * 60)))
    data[:, 3] = time
    data2.HORA = time2

    keys = []  # keys sera un arreglo que contendra todos los codigos de los camiones
    for i in range(len(data2.HORA)):
        if data2.CODIGO[i] not in keys:  # si el codigo no esta en el arreglo se agrega
            keys.append(data2.CODIGO[i])

    result = []  # result contendra toda la informacion que se va a necesitar
    # k=0
    for i in range(len(keys)):
        d = data[((data[:, 0] == keys[i]))]  # crea un subset de la matriz tomando solo el codigo de la posicion i
        tiempo = timedelta()  # inicializa el tiempo en 0
        dist = 0  # inicializa la distancia en 0
        c = pd.DataFrame({'CODIGO': d[:, 0], 'FECHA': d[:, 2], 'HORA': d[:, 3], 'LATITUD': d[:, 4], 'LONGITUD': d[:,
                                                                                                                5]})  # ,'VELOCIDAD':d[:,5], 'MES':d[:, 6]}) #se reconvierte el numpy array a pandas dataframe porque es mas sencillo de manipular; hacer el subset en numpy permite indexar adecuadamente
        for j in range(len(c.HORA) - 1):
            if ((datetime.strptime(str(c.HORA[j + 1]), '%H:%M:%S') - datetime.strptime(str(c.HORA[j]), '%H:%M:%S')) < (
                        datetime.strptime(tbt, '%M:%S') - datetime.strptime('00:00', '%M:%S')) and (
                        c.FECHA[j + 1] == c.FECHA[j])):
                # Si la diferencia entre dos coordenadas inmediatas del mismo camion es menor a 10 minutos y las coordenadas son del mismo dia:
                tiempo = tiempo + (datetime.strptime(str(c.HORA[j + 1]), '%H:%M:%S') - datetime.strptime(str(c.HORA[j]),
                                                                                                         '%H:%M:%S'))  # Acumula el tiempo
                orig_coord = (
                    c.LATITUD[j], c.LONGITUD[j])  # Obtiene las coordenadas de latitud y longitud del primer punto
                dest_coord = (
                    c.LATITUD[j + 1],
                    c.LONGITUD[j + 1])  # Obtiene las coordenadas de latitud y longitud del segundo punto
                dist = dist + (
                    vincenty(orig_coord, dest_coord).kilometers)  # Calcula la distancia en metros entre ambos puntos
                if c.CODIGO[j + 1] == '11FB5201' and c.FECHA[j + 1] == '25/10/2014':
                    print (vincenty(orig_coord, dest_coord).meters)
                    print [orig_coord, dest_coord]
            else:
                if (c.FECHA[j + 1] != c.FECHA[j]) and tiempo.seconds > 0:  # Si se cambia de fecha:
                    result.append([c.FECHA[j], str(tiempo.seconds // 3600) + ':' + str((tiempo.seconds // 60) % 60),
                                   tiempo.seconds / float(3600), dist, dist / (tiempo.seconds / float(3600)), c.CODIGO[
                                       j]])  # , c.MES[j]]) #Agrega a la base de datos final el acumulado del dia anterior al que va a llegar
                    tiempo = timedelta()
                    dist = 0  # Se reinicializa tiempo y distancia
        if (len(
                c.CODIGO) > 1) and tiempo.seconds > 0:  # Si se acaban todas las entradas para el camion y hay mas de una sola entrada, se adjunta la informacion de la ultima fecha a la base de datos
            result.append([c.FECHA[j], str(tiempo.seconds // 3600) + ':' + str((tiempo.seconds // 60) % 60),
                           tiempo.seconds / float(3600), dist, dist / (tiempo.seconds / float(3600)),
                           c.CODIGO[j]])  # , c.MES[j]])


    # result = concat([Solution, coords], axis=1)

    result = pd.DataFrame(
        result)  # .to_csv("estadisticasGPS.csv", header=['Fecha', 'Tiempo', 'Duracion', 'Distancia', 'Velocidad', 'Codigo', 'Mes'], index=False) #Se guarda el resultado en un archivo llamado estadisticasGPS
    result.columns = ['fecha', 'tiempo', 'duracion', 'distancia', 'velocidad', 'codigo']  # , 'mes']
    result2 = result

    # CO2 emissions
    utiliz = pd.read_csv(co2)
    listav = []
    hallado = 0
    for i in range(len(result2)):
        if hallado != 1 and i != 0:
            print ('no halle ' + str(result2.codigo[i - 1]), str(result2.fecha[i - 1]))
            listav.append('NOT FOUND')
        hallado = 0
        for j in range(len(utiliz)):
            if result2.codigo[i] == utiliz.CODIGO[j] and str(result2.fecha[i][0:2] + '/' + result2.fecha[i][3:5] + '/' +
                                                                     result2.fecha[i][6:10]) == utiliz.FECHA[j]:
                listav.append(utiliz.UTILIZACION[j])
                hallado = 1

    capacidad = pd.read_csv(capacity_input)
    listac = []
    hallado = 0
    for i in range(len(result2)):
        if hallado != 1 and i != 0:
            print ('no halle ' + str(result2.codigo[i - 1]), str(i - 1))
            listac.append('NOT FOUND')
        hallado = 0
        for j in range(len(capacidad)):
            if str(result2.codigo[i]) == str(capacidad.CODIGO[j]):
                listac.append([capacidad.CAPACIDAD[j]])
                hallado = 1

    hallado = 0
    fuel = pd.read_csv(fuel_input)
    fc = []
    for i in range(len(listac)):
        if hallado != 1 and i != 0:
            print i
            fc.append('NOT FOUND')
        hallado = 0
        for j in range(len(fuel)):
            if listac[i] == fuel.Size[j]:
                fc.append([fuel.FCempty[j], fuel.FCfull[j]])
                hallado = 1

    TE = []
    for i in range(len(fc)):
        try:
            TE.append(2.615 * result2.distancia[i] * (fc[i][0] + ((fc[i][1] - fc[i][0]) * float(listav[i]))))
        except TypeError:
            TE.append('Missing information')
        except ValueError:
            TE.append('Missing information')

    TE = pd.DataFrame(TE)
    TE.columns = ['emissions']
    database = pd.concat([result, TE], axis=1)

    #pd.DataFrame(database).to_csv(output, index=False)
    pd.DataFrame(database).to_csv(stats, index=False)
    pd.DataFrame(data2).to_csv(traces, index=False)


def main(argv):
    output = "output.csv"
    traces_output = "traces.csv"

    input = "input.csv"
    co2_input = "co2.csv"
    capacity_input = "capacity.csv"
    fuel_input = "fuel.csv"
    stats = "stats.csv"

    polygon_file_name = "polygon.csv"

    first_column_name = "CODIGO"
    last_column_name = "TEMPERATURA 2"

    hash_name = ''.join(random.choice(string.ascii_uppercase) for i in range(24))

    try:
        opts, args = getopt.getopt(argv, "i:o:p:f:l:t:c:a:u:s:y:",
                                   ["input=", "output=", "polygon=", "first_column=", "last_column=", "time_delta=",
                                    "co2=", "capacity=", "fuel=", 'stats=', "traces="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-f", "--first_column"):
            first_column_name = arg
        elif opt in ("-l", "--last_column"):
            last_column_name = arg
        elif opt in ("-p", "--polygon"):
            polygon_file_name = arg
        elif opt in ("-t", "--time_delta"):
            time_delta = arg
        elif opt in ("-c", "--co2"):
            co2_input = arg
        elif opt in ("-a", "--capacity"):
            capacity_input = arg
        elif opt in ("-u", "--fuel"):
            fuel_input = arg
        elif opt in ("-s", "--stats"):
            stats = arg
        elif opt in ("-y", "--traces"):
            traces_output = arg

    timebettraces = '02:00'
    # Time between consecutive GPS traces that will be used as a parameter to decide
    # if the truck remained within the square kilometer in the lapse between the two traces

    SecondFilter(input, polygon_file_name, hash_name, first_column_name, last_column_name, timebettraces)
    process(hash_name, fuel_input, capacity_input, co2_input, output, stats, traces_output, first_column_name,
            last_column_name, timebettraces)

    os.remove(hash_name)


if __name__ == "__main__":
    main(sys.argv[1:])
