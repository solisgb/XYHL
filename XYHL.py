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
    from os.path import join
    import pyodbc
    import db_con_str

    db = project.find('db').text
    con = pyodbc.connect(db_con_str.con_str(db))

    cur = con.cursor()
    select_master = project.find('select_master').text.strip()
    cur.execute(select_master)

    select_data = project.find('select_data').text.strip()
    npar = select_data.count('?')
    if npar > 0:
        par_select_data_col = project.findall('select_master/parameter_select_data_column')
        if len(par_select_data_col) != npar:
            raise ValueError('distinto número de ? en select_data que tags par_select_data_col')
        cols = [int(item.text)-1 for item in par_select_data_col]

    select_umbrales = project.find('select_umbrales').text.strip()
    if select_umbrales.count('?') != 1:
        raise ValueError('select_umbrales debe tener un solo ?')

    cur2 = con.cursor()
    fecha_col = int(project.find('select_data').get('fecha_column'))-1
    value_col = int(project.find('select_data').get('value_column'))-1
    dir_out = project.find('dir_out').text.strip()
    ylabel = project.find('graph').get('y_axis_name')
    for row in cur:

        params = tuple([row[col] for col in cols])
        cur2.execute(select_data, params)
        xy = [(row_data[fecha_col], row_data[value_col]) for row_data in cur2]
        nd = len(xy)
        if nd > 1:
            print('{0} tiene {1:d} datos entre {2} y {3}'.format(row[cols[0]],
                  nd, xy[0][0].strftime('%d/%m/%Y'),
                  xy[-1][0].strftime('%d/%m/%Y')))
        else:
            print('{0} tiene {1:d} datos'.format(row[cols[0]], nd))
            continue
        fechas = [xy1[0] for xy1 in xy]
        values = [xy1[1] for xy1 in xy]

        cur2.execute(select_umbrales, params)

        ufechas= ufechas_get(project, row, fechas)

        stitle = get_title(project, row)
        legends = legends_get(project, row)
        file_name = file_name_get(project, row)
        dst = join(dir_out, file_name)

#        XYt_1(fechas, values, ufechas, stitle, ylabel, legends, dst)

    con.close()


def get_title(project, row):
    """
    forma el título del gráfico
    """
    titles = project.findall('graph/title')
    if len(titles) == 0:
        return ""
    stitles = [title.text.strip() for title in titles]
    for i, title in enumerate(titles):
        cols = title.findall('column')
        if len(cols) == 0:
            continue
        subs = [row[int(col.text)-1] for col in cols]
        stitles[i] = stitles[i].format(*subs)
    return '\n'.join(stitles)


def legends_get(project, row):
    """
    forma las leyendas del gráfico
    """
    legends = project.findall('graph/legend')
    if len(legends) != 2:
        raise ValueError('El número de tags legend debe ser 2')
    slegends, columns = zip(*[[legend.get('text'),
                      int(legend.get('column'))-1] for legend in legends])
    slegends = list(slegends)
    for i, column in enumerate(columns):
        slegends[i] = slegends[i].format(row[column])
    return slegends


def file_name_get(project, row):
    """
    forma el nombre de cada fichero de gráfico
    """
    fname = project.find('select_master/file_name').text.strip()
    tcols = project.findall('select_master/file_name/column')
    subs = [row[int(tcol.text)-1] for tcol in tcols]
    sname = fname.format(*subs)
    return sname


def ufechas_get(project, row, fechas):
    """
    forma la lista de fechas de los umbrales
    """
    pass


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
