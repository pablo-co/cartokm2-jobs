__author__ = ''

from gurobipy import *
import pandas as pd
import numpy as np
import os
from pandas import concat
from filesearcher import filesearcher


def process(frequencies_file):
    stdmean = pd.read_csv('./5StopsCentroids/Output/StdAndMean.csv')
    os.chdir('./7FLM/')
    TS = np.genfromtxt('./Input/demand.csv', dtype=None, delimiter=',')

    costmatrix = np.genfromtxt('./Input/DistanceStopsToCustomers.csv', dtype=None, delimiter=',')

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

    filesearcher()

    codes = pd.read_csv(frequencies_file)

    plotlycodes = []
    link = []
    for i in range(len(costmatrix)):
        link.append('https://plot.ly/~rafaeles/' + str(plotlycodes[i]) + '.png')

    Solution.columns = ['p' + str(i) for i in range(len(costmatrix))]
    os.chdir(os.path.dirname(os.getcwd()))
    centr = pd.read_csv('./6DistanceMatrices/Input/Centroids.csv')
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
    pd.DataFrame(result).to_csv(
        "./8Optimization/Input/SolutionFLM2.csv")  # , header=['p'+str(i) for i in range(len(costmatrix)), 'latitud', 'longitud'])
    pd.DataFrame(result).to_csv("./Km2Datasets/Scenario/Km2Solution.csv")
    pd.DataFrame(stopsdataset).to_csv('./Km2Datasets/Stops/Km2Stops.csv', index=False)
