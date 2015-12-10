import sys
import traceback
from bhulan.processVehicles import importTrucks, initCompute
from bhulan.processStops import saveComputedStops
from bhulan.util import notify, getTime
from pymongo import MongoClient
from bhulan.constants import WATTS_DATA_DB_KEY
from bhulan.inputOutput import saveStopsToFile
import numpy as np
from bhulan.merger import merger
import getopt
import warnings
import string
import random

db = WATTS_DATA_DB_KEY


def trucks(filename):
    importTrucks(filename=filename)


def compute():
    initCompute()


def stops():
    saveComputedStops()
    return 0


def run(func, args):
    messages = {
        trucks: "import trucks ",
        compute: "compute truck dates and centers ",
        stops: "compute stops and properties"
    }
    message = messages[func]

    try:
        getTime(func, message, *args)
        # func(*args)
        # notify(message)
    except:
        print traceback.format_exc()
        notify(message + "failed")


def setupAll(input_file_name):
    try:
        run(trucks, [input_file_name])
        run(compute, [])
        run(stops, [])
        notify("complete setup succeeded!")
    except:
        print traceback.format_exc()
        notify("complete setup failed...")


##
# deletes the database and cleans up the collections
def dataPurge(db):
    client = MongoClient()
    client.drop_database(db)


def main(argv):
    input_file_name = "input.csv"
    output_file_name = "output.csv"
    existing_file_name = "existing.csv"
    non_existing_file_name = "non_existing.csv"

    hash_name = ''.join(random.choice(string.ascii_uppercase) for i in range(24))

    try:
        opts, args = getopt.getopt(argv, "i:o:e:n:", ["input=", "output=", "existing=", "non_existing="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_file_name = arg
        elif opt in ("-e", "--existing"):
            existing_file_name = arg
        elif opt in ("-n", "--non_existing"):
            non_existing_file_name = arg
        elif opt in ("-o", "--output"):
            output_file_name = arg

    dataPurge(db)
    setupAll(input_file_name)
    run(trucks, [input_file_name])
    run(stops, [])
    run(compute, [])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        exc = np.array([])
        try:
            exc = np.genfromtxt(non_existing_file_name, dtype=None, delimiter=',')
        except:
            print 'Non existing empty'

        exist = np.genfromtxt(existing_file_name, dtype=None, delimiter=',')
        i = exist.min()
        while i < (exist.max() + 1):
            if i not in exc:
                saveStopsToFile(hash_name, i)
            i += 1




    # saveStopsToFile(216)

    # if len(sys.argv) == 2:
    #    if sys.argv[1] == "all":
    #        getTime(setupAll, "Ran complete setup")
    #    if sys.argv[1] == "trucks":
    #        run(trucks, [])
    #    if sys.argv[1] == "stops":
    #        run(stops, [])
    #    if sys.argv[1] == "compute":
    #        run(compute, [])

    merger(existing_file_name, output_file_name, hash_name)

if __name__ == "__main__":
    main(sys.argv[1:])
