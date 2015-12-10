import os
from pandas import concat
import numpy as np
global dffinald
global k
import pandas as pd
import sys
import getopt


def process(std_and_mean_file_name, centroids_file_name, demand_file_name, distance_to_customers_file_name, output_file_name):
    stdmean = pd.read_csv(std_and_mean_file_name)
    TS = np.genfromtxt(demand_file_name, dtype=None, delimiter=',')
    costmatrix = np.genfromtxt(distance_to_customers_file_name, dtype=None, delimiter=',')

    objectivemat = []
    PPS = range(len(costmatrix))
    Solution = pd.DataFrame(index=PPS, columns=range(len(costmatrix)))
    Solution = Solution.fillna(0)

    for k in range(1, len(costmatrix) + 1):

        # Facility location model (FLM)
        m = Model('FLM1.1')
        # Parking spots (max)
        PS = k
        # initialize objective function
        obj = 0
        # Potential parking stops


        # Actual stops
        Potspot = []

        # Create decision variables
        for i in PPS:
            Potspot.append(m.addVar(vtype=GRB.BINARY, name="Chosen_Spots%d" % i))

        transport = []
        for i in PPS:
            transport.append([])
            for j in range(len(TS)):
                transport[i].append(m.addVar(vtype=GRB.INTEGER, name="Trans%d.%d" % (i, j)))

        m.modelSense = GRB.MINIMIZE
        m.update()

        # Objective function
        for i in PPS:
            for j in range(len(TS)):
                obj = TS[j] * costmatrix[i][j] * transport[i][j] + obj

        m.setObjective(obj)

        # Constrains
        for j in range(len(TS)):
            m.addConstr(quicksum((transport[i][j] for i in PPS)) >= 1, name="Next_spot%d" % j)

        for i in PPS:
            for j in range(len(TS)):
                m.addConstr((transport[i][j] - Potspot[i]) <= 0, "Link%d.%d" % (i, j))

        for i in PPS:
            m.addConstr((Potspot[i] - quicksum(transport[i][j] for j in range(len(TS)))) <= 0, "Link%d.%d" % (i, j))

        m.addConstr(quicksum(Potspot[i] for i in PPS) == PS, "Max_spots%d")

        m.optimize()
        m.getObjective()
        objectivemat.append(m.objVal)
        for i in PPS:
            Solution[k - 1][i] = Potspot[i].x
            print(k, i)
        # m.write('FLM1.11.lp')
        if k == len(costmatrix):
            clients = []
            dropsize = []
            droppercl = []
            durpercl = []
            for i in PPS:
                clients.append(0)
                dropsize.append(0)
                droppercl.append(0)
                durpercl.append(0)
                for j in range(len(TS)):
                    dropsize[i] = TS[j] * transport[i][j].x + dropsize[i]
                    clients[i] = clients[i] + transport[i][j].x
                droppercl[i] = dropsize[i] / clients[i]
                durpercl[i] = stdmean.Mean[i] / clients[i]

    plotlycodes=init()

    link = []
    for i in range(len(costmatrix)):
        link.append(str(plotlycodes[i]) + '.png')

    Solution.columns = ['p' + str(i) for i in range(len(costmatrix))]

    centr = pd.read_csv(centroids_file_name)
    coords = centr[['latitud', 'longitud']]
    result = concat([Solution, coords], axis=1)

    dropsize = pd.DataFrame(dropsize)
    droppercl = pd.DataFrame(droppercl)
    clients = pd.DataFrame(clients)
    durpercl = pd.DataFrame(durpercl)
    link = pd.DataFrame(link)

    stopsdataset = concat([coords, stdmean, dropsize, droppercl, clients, durpercl, link], axis=1)
    stopsdataset.columns = ['latitud', 'longitud', 'sigma', 'mean_duration', 'drop_size_per_number_of_clientes',
                            'dropsize_per_stop', 'clientes', 'duration_per_number_of_clients', 'link']

    pd.DataFrame(stopsdataset).to_csv(output_file_name, index=False)


def main(argv):
    std_and_mean_file_name = "std_and_mean_file_name.csv"
    demand_file_name = "demand_file_name.csv"
    centroids_file_name = "centroids_file_name.csv"
    distance_to_customers_file_name = "distance_to_customers_file_name.csv"
    output_file_name = "output_file_name.csv"

    try:
        opts, args = getopt.getopt(argv, "q:d:c:o:",
                                   ["std_and_mean=", 'frequencies=', "centroids=", "demand=", "distance_to_customers", "output="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-q", "--std_and_mean"):
            std_and_mean_file_name = arg
        elif opt in ("-d", "--centroids"):
            centroids_file_name = arg
        elif opt in ("-d", "--demand"):
            demand_file_name = arg
        elif opt in ("-c", "--distance_to_customers"):
            distance_to_customers_file_name = arg
        elif opt in ("-o", "--output"):
            output_file_name = arg

    process(std_and_mean_file_name, centroids_file_name, demand_file_name, distance_to_customers_file_name, output_file_name)
