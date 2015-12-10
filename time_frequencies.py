
import numpy as np
from shapely.geometry import Point
import pandas as pd
import numpy as np
import statistics as st
from shapely.geometry import Polygon
import os
import numpy
from gurobipy import *
import os
from pandas import concat
import getopt
import sys
import plotly.plotly as py
from plotly.graph_objs import *


def process(frequencies_file_name, std_and_mean_file_name, centroids_file_name, demand_file_name,
            distance_to_customers_file_name, output_file_name):
    a = np.genfromtxt(frequencies_file_name, dtype=None, delimiter=',')
    b = []
    c = []
    for i in range(1, len(a)):
        b.append(list(a[i])[0:24])
        # print b
        c.append([])
        for j in range(len(b[i - 1])):
            c[i - 1].append(int(b[i - 1][j]))

    py.sign_in('rafaeles', 'fawg2muzga')

    urls = []

    for i in range(len(c)):
        data = Data([
            Scatter(
                x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                y=c[i],
                name='Stops along the day',
                error_y=ErrorY(
                    color='rgb(0,116,217)',
                    thickness=1,
                    width=1
                ),
                error_x=ErrorX(
                    copy_ystyle=True
                ),
                marker=Marker(
                    color='rgb(0,116,217)',
                    size=8,
                    symbol='circle',
                    line=Line(
                        color='white',
                        width=6
                    )
                ),
                line=Line(
                    color='rgb(34, 34, 34)',
                    width=8,
                    dash='solid',
                    shape='hv'
                ),
                connectgaps=True,
                fill='none',
                opacity=1,
                visible=True,
                xsrc='rafaeles:87:cb11cd',
                ysrc='rafaeles:87:4e1bc5'
            )
        ])
        layout = Layout(
            title='<br>Frequency',
            titlefont=Font(
                family='',
                size=0,
                color=''
            ),
            font=Font(
                family='"Droid Sans", sans-serif',
                size=12,
                color='rgb(33, 33, 33)'
            ),
            showlegend=True,
            autosize=False,
            width=725,
            height=600,
            xaxis=XAxis(
                title='Time of the day',
                titlefont=Font(
                    family='',
                    size=0,
                    color=''
                ),
                range=[-0.1, 24.1],
                domain=[0.1, 1],
                type='linear',
                rangemode='normal',
                autorange=False,
                showgrid=False,
                zeroline=False,
                showline=True,
                nticks=15,
                ticks='inside',
                showticklabels=True,
                tick0=0,
                dtick=1,
                ticklen=5,
                tickwidth=1,
                tickcolor='#000',
                tickangle='auto',
                tickfont=Font(
                    family='',
                    size=0,
                    color=''
                ),
                exponentformat='e',
                showexponent='all',
                mirror='allticks',
                gridcolor='#ddd',
                gridwidth=1,
                zerolinecolor='#000',
                zerolinewidth=1,
                linecolor='rgb(34,34,34)',
                linewidth=1,
                anchor='y',
                overlaying=False,
                position=0
            ),
            yaxis=YAxis(
                title='',
                titlefont=Font(
                    family='',
                    size=0,
                    color=''
                ),
                range=[0, max(c[i])],
                domain=[0, 1],
                type='linear',
                rangemode='tozero',
                autorange=True,
                showgrid=False,
                zeroline=False,
                showline=True,
                nticks=0,
                ticks='inside',
                showticklabels=False,
                tick0=0,
                dtick=10,
                ticklen=5,
                tickwidth=1,
                tickcolor='#000',
                tickangle='auto',
                tickfont=Font(
                    family='',
                    size=0,
                    color=''
                ),
                exponentformat='none',
                showexponent='all',
                mirror='allticks',
                gridcolor='#ddd',
                gridwidth=1,
                zerolinecolor='#000',
                zerolinewidth=1,
                linecolor='rgb(34,34,34)',
                linewidth=1,
                anchor='x',
                overlaying=False,
                side='right',
                position=0
            ),
            annotations=Annotations([
                Annotation(
                    x=0.11416096350027202,
                    y=0.3,
                    xref='paper',
                    yref='paper',
                    text='',
                    showarrow=True,
                    font=Font(
                        family='Raleway, sans-serif',
                        size=16,
                        color='rgb(33, 33, 33)'
                    ),
                    xanchor='auto',
                    yanchor='auto',
                    align='center',
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=0,
                    arrowcolor='rgba(0, 0, 0, 0)',
                    ax=479,
                    ay=-227.5,
                    bordercolor='',
                    borderwidth=1,
                    borderpad=1,
                    bgcolor='rgba(0, 0, 0, 0)',
                    opacity=1
                )
            ]),
            margin=Margin(
                l=80,
                r=80,
                b=80,
                t=100,
                pad=2,
                autoexpand=True
            ),
            paper_bgcolor='white',
            plot_bgcolor='rgb(255, 255, 255)',
            hovermode='x',
            dragmode='zoom',
            separators='.,',
            barmode='stack',
            bargap=0.2,
            bargroupgap=0,
            boxmode='overlay',
            boxgap=0.3,
            boxgroupgap=0.3,
            hidesources=False,
            yaxis2=YAxis(
                title='Frequency',
                range=[0, max(c[i])],
                autorange=False,
                overlaying='y',
                side='left',
                position=0
            )
        )
        fig = Figure(data=data, layout=layout)
        plot_url = py.plot(fig)
        urls.append(plot_url)

    # pd.DataFrame(urls).to_csv(output_file_name, index=False, header=['frequency'])

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
            for i in range(min(len(costmatrix), len(stdmean.Mean))):
                clients.append(0)
                dropsize.append(0)
                droppercl.append(0)
                durpercl.append(0)
                for j in range(len(TS)):
                    dropsize[i] = TS[j] * transport[i][j].x + dropsize[i]
                    clients[i] = clients[i] + transport[i][j].x
                droppercl[i] = dropsize[i] / clients[i]
                print "i " + str(i)
                print stdmean.Mean
                print stdmean.Mean[i]
                durpercl[i] = stdmean.Mean[i] / clients[i]

    plotlycodes = urls

    link = []
    for i in range(len(plotlycodes)):
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
    frequencies_file_name = "frequencies_file_name.csv"
    output_file_name = "output_file_name.csv"

    try:
        opts, args = getopt.getopt(argv, "q:f:c:d:u:o:",
                                   ["std_and_mean=", 'frequencies=', "centroids=", "demand=", "distance_to_customers=",
                                    "output="])
    except getopt.GetoptError, exc:
        print exc.msg
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-q", "--std_and_mean"):
            std_and_mean_file_name = arg
        elif opt in ("-f", "--frequencies"):
            frequencies_file_name = arg
        elif opt in ("-c", "--centroids"):
            centroids_file_name = arg
        elif opt in ("-d", "--demand"):
            demand_file_name = arg
        elif opt in ("-u", "--distance_to_customers"):
            distance_to_customers_file_name = arg
        elif opt in ("-o", "--output"):
            output_file_name = arg

    process(frequencies_file_name, std_and_mean_file_name, centroids_file_name, demand_file_name, distance_to_customers_file_name,
            output_file_name)


if __name__ == "__main__":
    main(sys.argv[1:])
