import pandas
import sys
import getopt


def read_data_from_file(file_name):
    return pandas.read_csv(file_name)


def export_dataset(dataset, output):
    pandas.DataFrame(dataset).to_csv(output, index=False, header=None)


def process_traces(data, dates, output_file_name):
    result = []
    for i in range(len(dates)):
        subs = data[data.FECHA == dates.Fecha[i]]  # Creates a subset for each day
        subs = subs.reset_index(drop=True)  # Resets pandas dataframe indexe
        if len(subs) > 1:
            result.append(int(dates.Fecha[i][3:5]) * 31 + int(dates.Fecha[i][0:2]))  # Finds coded dates

    data.reset_index(drop=True)
    writer = pandas.ExcelWriter(output_file_name, engine='xlsxwriter')  # Writes data into xlsx format
    data.to_excel(writer, sheet_name='Hoja1', index=False)

    return result


def get_exceptions(dates):
    exceptions = []
    for i in range(min(dates), max(dates)):
        if i not in dates:
            exceptions.append(i)  # finds which dates do not have any registered GPS activity

    return exceptions


def main(argv):
    output = "output.xlsx"
    input_file_name = "input.csv"
    dates_file_name = "dates.csv"
    existing_file_name = "existing.csv"
    non_existing_file_name = "non_existing.csv"

    try:
        opts, args = getopt.getopt(argv, "i:d:o:e:n:",
                                   ["input=", "dates=", "output=", "existing=", "non_existing="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_file_name = arg
        elif opt in ("-d", "--dates"):
            dates_file_name = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-e", "--existing"):
            existing_file_name = arg
        elif opt in ("-n", "--non_existing"):
            non_existing_file_name = arg

    traces_data = read_data_from_file(input_file_name)
    dates_data = read_data_from_file(dates_file_name)

    dates_processed_data = process_traces(traces_data, dates_data, output)
    exceptions_data = get_exceptions(dates_processed_data)

    export_dataset(dates_processed_data, existing_file_name)
    export_dataset(exceptions_data, non_existing_file_name)


if __name__ == "__main__":
    main(sys.argv[1:])
