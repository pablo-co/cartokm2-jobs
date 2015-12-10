import xlrd
import csv
import sys
import getopt


def open_sheet(file, sheet_name):
    return file.sheet_by_name(sheet_name)


def open_file(file_name):
    return xlrd.open_workbook(file_name)


def create_file(file_name):
    return open(file_name, 'wb')


def create_file_writer(file):
    return csv.writer(file, quoting=csv.QUOTE_ALL)


def convert(input_file_name, output_file_name, sheet):
    # Open xlsx data
    input_file = open_file(input_file_name)
    input_sheet = open_sheet(input_file, sheet)

    # Create output file
    output_file = create_file(output_file_name)
    output_file_writer = create_file_writer(output_file)

    for rownum in range(input_sheet.nrows):
        # Takes the date that will be changed to another format
        date = input_sheet.row_values(rownum)[2]
        # Did the date format change?
        if isinstance(date, float) or isinstance(date, int):
            # Keep original date format
            year, month, day, hour, minute, sec = xlrd.xldate_as_tuple(date, input_file.datemode)
            py_date = "%02d-%02d-%04d" % (day, month, year)

            output_file_writer.writerow(
                input_sheet.row_values(rownum)[0:2] + [py_date] + input_sheet.row_values(rownum)[3:])
        else:
            output_file_writer.writerow(input_sheet.row_values(rownum))

    output_file.close()


def main(argv):
    output = "output.csv"
    input = "input.xlsx"
    sheet_name = "Hoja1"
    try:
        opts, args = getopt.getopt(argv, "i:o:s:d", ["input=", "output=", "sheet="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-s", "--sheet"):
            sheet_name = "Hoja 1"

    convert(input, output, sheet_name)


if __name__ == "__main__":
    main(sys.argv[1:])
