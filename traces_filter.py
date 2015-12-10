import pandas
from shapely.geometry import Point
from shapely.geometry import Polygon
import matplotlib.pyplot as pyplot
import sys
import getopt


def read_data_from_file(file_name):
    return pandas.read_csv(file_name)


def load_polygon(file):
    coordinates = []
    for i in range(len(file.latitud)):
        coordinates.append((file.latitud[i], file.longitud[i]))
    return Polygon(coordinates)


def plot(x, y):
    pyplot.plot(y, x)


def get_filtered_data(data, square_km, first_column_name, last_column_name):
    resulting_data = []
    unique_dates = []

    for i in range(len(data.LATITUD)):
        coordinate = Point(data.LATITUD[i], data.LONGITUD[i])
        if square_km.contains(coordinate):
            resulting_data.append(data.ix[i][first_column_name:last_column_name])
            if data.FECHA[i] not in unique_dates:
                unique_dates.append(data.FECHA[i])

    return resulting_data, unique_dates


def export_dataset(dataset, output, header=None):
    if header == None:
        pandas.DataFrame(dataset).to_csv(output, index=False)
    else:
        pandas.DataFrame(dataset).to_csv(output, index=False, header=header)


def main(argv):
    input = "input.csv"
    output = "output.csv"
    output_dates = "dates.csv"
    polygon_file_name = "polygon.csv"

    first_column_name = "CODIGO"
    last_column_name = "TEMPERATURA 2"

    try:
        opts, args = getopt.getopt(argv, "i:o:p:d:f:l:t",
                                   ["input=", "output=", "polygon=", "dates=", "first_column=", "last_column="])
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
        elif opt in ("-d", "--dates"):
            output_dates = arg

    polygon_file = pandas.read_csv(polygon_file_name)
    polygon = load_polygon(polygon_file)

    buffered_square_km = polygon.buffer(5 / 3600.0)

    plot(*polygon.exterior.xy)
    plot(*buffered_square_km.exterior.xy)

    data = read_data_from_file(input)

    resulting_data, dates = get_filtered_data(data, buffered_square_km, first_column_name, last_column_name)

    dataset = pandas.DataFrame(resulting_data).drop_duplicates()

    export_dataset(dataset, output)
    export_dataset(dates, output_dates, header=['Fecha'])


if __name__ == "__main__":
    main(sys.argv[1:])
