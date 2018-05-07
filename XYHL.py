# -*- coding: Latin-1 -*-
"""
Created on Tue May  1 10:54:23 2018

@author: solis
"""


def select_project(FILENAME):
    """
    returns the selected project
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(FILENAME)
    root = tree.getroot()

    print('Projects in ' + FILENAME)
    projects = []
    for i, project in enumerate(root.findall('project')):
        projects.append(project)
        print(i, end=' ')
        print('. ' + project.get('name'))
    print('Select project number:')
    choice = input()
    return projects[int(choice)]


def make_graphs(project):
    """
    select data
    call graph maker
    """
    import pyodbc
    import db_con_str

    db = project.find('db').text
    con = pyodbc.connect(db_con_str.con_str(db))

    cur = con.cursor()
    select_master = project.find('select_master').text
    cur.execute(select_master)

    select_data = project.find('select_data').text
    npar = select_data.count('?')
    if npar > 0:
        par_select_data_col = project.findall('select_master/parameter_select_data_column')
        if len(par_select_data_col) != npar:
            raise ValueError('distinto número de ? en select_data que tags par_select_data_col')
    cols = [int(item.text)-1 for item in par_select_data_col]

    cur2 = con.cursor()
    fecha_col = int(project.find('select_data').get('fecha_column'))
    value_col = int(project.find('select_data').get('value_column'))
    for row in cur:
        print(row[cols[0]])
        params = tuple([row[col] for col in cols])
        data = cur2.execute(select_data, params)
        fechas = [data1[fecha_col] for data1 in data]
        values = [data1[value_col] for data1 in data]

        XYt_1(fechas, values, stitle, ylabel, dst)

    con.close()


def get_title(project):
    """
    forma el título del gráfico
    """
    titles = project.findall('graph/title')
    if len(titles) == 0:
        return ""
    stitles = [title.text for title in titles]
    for i, title in titles:
        cols = title.findall('column')
        if len(cols) == 0:
            continue






def XYt_1(xdate, y, stitle, ylabel, dst):
    """
    XY x datetime serie, y serie
    """

#    import datetime
#    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    dateFmt = mdates.DateFormatter('%m/%Y')

    fig, ax = plt.subplots()
    ax.plot(xdate, y)

    plt.grid(True)
    plt.ylabel(ylabel)

    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # use a more precise date string for the x axis locations in the
    # toolbar
    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)

    plt.tight_layout()
    fig.savefig(dst)
    plt.close('all')
