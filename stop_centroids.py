from shapely.geometry import Point
import pandas
import statistics as st
import numpy
import sys
import getopt


def process(input_file_name, frequencies_file_name, std_and_mean_file_name, centroids_file_name):
    data = numpy.genfromtxt(input_file_name, dtype=None, delimiter=',')

    base = []
    for i in range(1, len(data)):
        base.append([float(data[i][2]), float(data[i][3]), int(data[i][4][0:2]) * 60 + int(data[i][4][3:5]),
                     data[i][1][11:]])  # Gets the data that will be useful from the stops algorithm output dataset

    base = pandas.DataFrame(base)  # Creates a dataset from this info
    base.columns = ['lat', 'lng', 'duration', 'time']  # Renames the columns

    base1 = []
    base13 = []
    lista = []
    lista2 = []
    duracion = []

    buffer_area = 0.0003  # The amount of degrees (lat long coordinates) separating two points considered in order to count them as the same point for cluster algorithm
    minfreq = 8  # The minimum number of times a stop must have been visited in order to count it as a regular stop
    iterations = 10

    for i in range(len(base.lat)):
        base1.append([base.lat[i], base.lng[i], base.duration[i], base.time[
            i]])  # appends the info into some other data structures that will be used for the cluster algorithms (they will change along the iterations)
        base13.append([base.lat[i], base.lng[i], base.duration[i], base.time[i]])
    # print len(base1)
    # We will search the points near each point, then calculate their centroid for every point. At the end, we will have many equal points which will be filtered in order to get the final centroids
    for p in range(iterations):
        print 'Currently running iteration ' + str(p + 1) + ' out of ' + str(iterations)
        lista = []
        for i in range(len(base1)):
            lista2 = []
            for j in range(len(base1)):
                if i != j:
                    point = Point(base1[i][0], base1[i][1])  # Gets lat and long of each stops point
                    area = point.buffer(buffer_area)  # Defines an area around that point
                    p2 = Point(base1[j][0], base1[j][1])  # Gets lat and long from all the other points in the dataset
                    q = area.contains(
                        p2)  # Checks whether each point is close enough from another one. If it is, then their lats and longs will be averaged in order to compute the centroids

                    if q == 1:
                        lista2.append(
                            j)  # Adds in the position of all the points that are within the considered distance
            lista.append(lista2)  # Pulls out all the positions for each point

        sumalat = 0
        sumalng = 0
        sumaduration = 0
        lista3 = []

        for i in range(len(lista)):
            sumalat = 0
            sumalng = 0
            sumaduration = 0
            k = 1
            if len(lista[i]) > 0:
                for j in range(len(lista[i])):
                    k = k + 1  # Counts the number of points that influence each centroid

                    sumalat = sumalat + base1[lista[i][j]][
                        0]  # Sums all lats of the points forming the cluster for every point
                    sumalng = sumalng + base1[lista[i][j]][
                        1]  # Sums all lats of the points forming the cluster for every point
                    sumaduration = sumaduration + base1[lista[i][j]][
                        2]  # Sums all the durations of the points forming the cluster for every point
                sumalat = sumalat + base1[i][0]  # Adds at the end the same info for the starting point of each centroid
                sumalng = sumalng + base1[i][1]
                sumaduration = sumaduration + base1[i][2]
                lista3.append([sumalat / k, sumalng / k, sumaduration / k,
                               base1[i][3]])  # We get the new information for the centroid in iteration p
            else:
                lista3.append([base1[i][0], base1[i][1], base1[i][2],
                               base1[i][3]])  # If the point is completly isolated, we only consider it
        # print(len(lista3),len(base1))
        base1 = lista3  # The computed centroids become the starting info for the next iteration

    for i in range(len(lista)):
        k = 1
        sumaduration = 0
        if len(lista[i]) > 0:
            for j in range(len(lista[i])):
                k = k + 1
                sumaduration = sumaduration + base13[lista[i][j]][
                    2]  # base13 was left unchanged throughout the iterations, so we search which initial points finally formed a centroid and calculate average durations out of those
            sumaduration = sumaduration + base13[i][2]
            duracion.append(sumaduration / float((len(lista[i]) + 1)))  # k)
        else:
            duracion.append(base13[i][2])
            # print sum(duracion)

    filteredstopslat = []
    filteredstopslng = []
    filteredstops = []
    # timesfilt=[]
    position = []
    # filteredstops.append(['Lat', 'Lng'])
    k = 0
    for i in range(len(base1)):
        if base1[i][0] not in filteredstopslat and base1[i][1] not in filteredstopslng:
            filteredstopslat.append([])  # Adds only lats for centroids that have not been repeated
            filteredstopslng.append([])  # Adds only long for centroids that have not been repeated
            filteredstopslat[k].append(base1[i][0])
            filteredstopslng[k].append(base1[i][1])
            filteredstops.append([base1[i][0], base1[i][1],
                                  1])  # Adds both lat and long and counts the number of times each stop was visited
            # timesfilt.append(timesoftheday[i]) #Adds the time of the day in which each centroid was visited
            position.append([])
            position[k].append(i)
            k = k + 1
            print 'Found centroid number ' + str(k)
        else:
            for j in range(len(filteredstops)):
                if base1[i][0] == filteredstops[j][0] and base1[i][1] == filteredstops[j][1]:
                    filteredstops[j][
                        2] += 1  # Sums each time a stops centroid is repeated, so it allows us to know hoy many times each stop was visited
                    position[j].append(i)

    durasdlist = []
    k = 1
    # standard deviation

    durasd = []
    timesoftheday = []
    means = []
    for i in range(len(position)):
        durasd.append([])
        timesoftheday.append([])
        # durasd[i].append(base13[position[i][0]][2])
        # timesoftheday[i].append(base13[position[i][0]][3])
        if len(position[i]) > 1:
            for j in range(len(position[i])):
                durasd[i].append(base13[position[i][j]][
                                     2])  # Creates a list of durations that will then allow us to calculate the standard deviation of each centroid's duration
                timesoftheday[i].append(
                    base13[position[i][j]][3])  # Creates a list of times of the day in which each stop was visited
            # sd=numpy.std(durasd)
            sd = st.stdev(durasd[i])
            durasdlist.append(sd)
            media = numpy.mean(durasd[i])
            means.append(media)
        else:
            durasdlist.append(0)
            means.append(base13[position[i][0]][2])

        print 'Obtaining standard deviation for stop ' + str(k) + ' out of ' + str(len(position))
        k = k + 1

    finalstops = []
    finaltimes = []
    stddevandmean = []
    for i in range(len(filteredstops)):
        if filteredstops[i][2] > minfreq:
            finalstops.append(filteredstops[i])  # Keeps only the stops visited a certain number of times
            finaltimes.append(
                timesoftheday[i])  # Keeps only the visiting time of the stops visited a certain number of times
            stddevandmean.append([durasdlist[i], means[i]])
        else:
            print 'Stop number ' + str(i) + ' was visited only ' + str(
                filteredstops[i][2]) + ' times, so it will not be considered a regular stop'

    freqbytime = []
    for i in range(len(finaltimes)):
        freqbytime.append([])  # Iterates each centroid
        for k in range(24):
            freqbytime[i].append(0)  # Iterates each hour of the day
            for j in range(len(finaltimes[i])):  # Iterates each recorded time
                if int(finaltimes[i][j][0:2]) >= k and int(finaltimes[i][j][0:2]) < (k + 1):
                    freqbytime[i][k] = freqbytime[i][
                                           k] + 1  # Stores the frequency of visit of each stop by time of the day
        freqbytime[i].append(len(finaltimes[i]))

    pandas.DataFrame(stddevandmean).to_csv(std_and_mean_file_name, index=False, header=['StandardDeviation', 'Mean'])
    pandas.DataFrame(finalstops).to_csv(centroids_file_name, index=False,
                                        header=['latitud', 'longitud', 'Frequency'])
    pandas.DataFrame(freqbytime).to_csv(frequencies_file_name, index=False,
                                        header=['ZeroToOne', 'OneToTwo', 'TwoToThree', 'ThreeToFour', 'FourToFive',
                                                'FiveToSix', 'SixToSeven', 'SevenToEigth', 'EigthToNine', 'NineToTen',
                                                'TenToEleven', 'ElevenToTwelve', 'TwelveToThirteen',
                                                'ThirteenToFourteen',
                                                'FourteenToFifteen', 'FifteenToSixteen', 'SixteenToSeventeen',
                                                'SeventeenToEighteen', 'EighteenToNineteen', 'NineTeenToTwenty',
                                                'TwentyToTwentyone', 'TwentyoneToTwenttwo', 'TwentytwoToTwentythree',
                                                'TwentythreeToTwentfour', 'Total'])


def main(argv):
    input_file_name = "input_file_name.csv"
    std_and_mean_file_name = "std_and_mean_file_name.csv"
    centroids_file_name = "centroids_file_name.csv"
    frequencies_file_name = "frequencies_file_name.csv"

    try:
        opts, args = getopt.getopt(argv, "s:f:c:i",
                                   ["std_and_mean=", 'frequencies=', "centroids=", "input="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-s", "--std_and_mean"):
            std_and_mean_file_name = arg
        elif opt in ("-c", "--centroids"):
            centroids_file_name = arg
        elif opt in ("-i", "--input"):
            input_file_name = arg
        elif opt in ("-f", "--frequencies"):
            frequencies_file_name = arg

    process(input_file_name, frequencies_file_name, std_and_mean_file_name, centroids_file_name)


if __name__ == "__main__":
    main(sys.argv[1:])
