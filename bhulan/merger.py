# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 16:00:48 2015

"""

import pandas as pd
import numpy as np
from init import *


def merger(existing_file_name, output_file_name, hash_name):
    print "existing: " + existing_file_name
    exist = np.genfromtxt(existing_file_name, dtype=None,
                          delimiter=',')  # reads in the dates that have information recorded on the stops
    stops = []
    min_v = exist.min()
    max_v = exist.max() + 1
    for i in range(min_v, max_v):
        try:
            print 'Integrating file ' + hash_name + "_" + str(i) + ".csv"
            newfile = np.genfromtxt(GPS_FILE_DIRECTORY  + hash_name + "_" + str(i) + ".csv", dtype=None, delimiter=',')
            for j in range(1, len(newfile)):
                if len(
                        newfile) != 7:  # Helps detect empty datasets(meaning no stops were recorded for that specific date), this files are read in 7 columns, each one according to the column title
                    stops.append(newfile[j])  # adds the rows of the dataset
                else:
                    if newfile[0][
                        0] != 'i':  # checks whether the file is actually empty, if it is not, then it writes the stops, if it is, it prints out that that file is empty
                        stops.append(newfile[j])
                    else:
                        print 'File ' + str(i) + ' is empty'
        except IOError:

            print 'I could not find ' + str(i)
    df = pd.DataFrame(stops)  # Creates a dataset from stops
    if (df.size > 0):
        df = df.drop_duplicates()  # Removes duplicates
        pd.DataFrame(df).to_csv(output_file_name, header=['id', 'datenum', 'lat', 'lng', 'duration', 'time', 'truckid'],
                                index=False)
