# -*- coding: Latin-1 -*-
"""
Created on Tue May  1 10:54:23 2018

@author: solis
"""

import log_file as lf


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
    if npar != 1:
        raise ValueError('select_data debe tener un signo ?')
    id_col = int(project.find('select_master').get('id_column')) - 1

    select_umbrales = project.find('select_umbrales').text.strip()
    if select_umbrales.count('?') != 3:
        raise ValueError('select_umbrales debe tener 3 signos ?')
    umbral_col = int(project.find('select_umbrales').get('umbral_column')) - 1

    cur2 = con.cursor()
    fecha_col = int(project.find('select_data').get('fecha_column')) - 1
    value_col = int(project.find('select_data').get('value_column')) - 1
    dir_out = project.find('dir_out').text.strip()
    ylabel = project.find('graph').get('y_axis_name')
    for row in cur:

        # datos de la serie
        print(row[id_col])
        cur2.execute(select_data, row[id_col])
        xy = [(row_data[fecha_col], row_data[value_col]) for row_data in cur2]
        if len(xy) == 0:
            print('{0} no tiene datos'.format(row[id_col]))
            continue
        fechas = [xy1[0] for xy1 in xy]
        values = [xy1[1] for xy1 in xy]

        # datos de los umbrales
        values_u = []
        legends_umbrales = []
        for i, umbral in enumerate(project.findall('select_umbrales/umbral')):
            parametro = umbral.get('parametro').strip()
            cod_u = umbral.get('cod').strip()
            cur2.execute(select_umbrales, (row[id_col], cod_u, parametro))
            row1_u = cur2.fetchone()
            if row1_u is None:
                msg = '{} no tiene umbral: {}, {}'.format(row[id_col],
                                                          cod_u, parametro)
                print(msg)
                lf.write(msg)
                continue
            values_u.append([row1_u[umbral_col], row1_u[umbral_col]])
            legends_umbrales.append(legends_umbrales_get(project, row1_u, i))
        if not values_u:
            print('{0} no tiene umbrales'.format(row[id_col]))
            continue
        # todos los umbrales se ponen en el rango de datos de cada sondeo
        # si se desea ponerlo en su rango específico debe escribirse una
        # función específica
        fechas_u = [fechas[0], fechas[-1]]

        stitle = get_title(project, row)
        legend_master = legend_master_get(project, row)
        file_name = file_name_get(project, row)
        dst = join(dir_out, file_name)

        XYt_1(fechas, values, legend_master, fechas_u, values_u,
              legends_umbrales, stitle, ylabel, dst)

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


def legend_master_get(project, row):
    """
    forma la leyenda de la serie principal del gráfico
    """
    legend_master = project.find('graph/legend_master').text.strip()
    columns_master = project.findall('graph/legend_master/column')
    if len(columns_master) == 0:
        return legend_master
    subs = [row[int(col1.text)-1] for col1 in columns_master]
    return legend_master.format(*subs)


def legends_umbrales_get(project, row1_u, ilegend):
    """
    forma la leyenda de uno de los umbrales
    """
    legend_tag = project.find('graph/legend_umbrales')
    legend_mold = legend_tag.text.strip()
    len_legend_mold = len(legend_mold)
    col_tags = legend_tag.findall('column')
    n_cols = len(col_tags)
    if len_legend_mold == 0:
        return 'Leg. {0:d}'.format(ilegend)
    else:
        if n_cols == 0:
            return legend_mold
        else:
            subs = [row1_u[int(col.text)-1] for col in col_tags]
            return legend_mold.format(*subs)


def file_name_get(project, row):
    """
    forma el nombre de cada fichero de gráfico
    """
    fname = project.find('select_master/file_name').text.strip()
    tcols = project.findall('select_master/file_name/column')
    subs = [row[int(tcol.text)-1] for tcol in tcols]
    sname = fname.format(*subs)
    return sname


def XYt_1(fechas, values, legend_master, fechas_u, values_u, legends_umbrales,
          stitle, ylabel, dst):
    """
    XY x datetime serie, y serie
    """
    import matplotlib.pyplot as mpl
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    dateFmt = mdates.DateFormatter('%d-%m-%Y')

    fig, ax = plt.subplots()
    ax.plot(fechas, values, marker='.', label=legend_master)
    for i, vu1 in enumerate(values_u):
        ax.plot(fechas_u, vu1, label=legends_umbrales[i])

    plt.ylabel(ylabel)
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)
    mpl.legend(loc='best', framealpha=0.5)
    mpl.legend(loc='best', framealpha=0.5)
    mpl.tight_layout()
    mpl.grid(True)

    fig.savefig(dst)
    plt.close('all')


# def fechas_u_get(row_u, fechas):
#    """
#    forma la lista de fechas de los umbrales
#    TODO: si se desea implementar hay que terminar de escribirla
#    ahora no funciona
#    """
#    fechas_u = []
#    for row_u1 in row_u:
#        fecha_u1 = None
#        for fecha1 in fechas:
#            if fecha1 >= row_u1[2]:
#                fecha_u1 = fecha1
#                break
#
#        if row_u1[3] is None:
#            fecha_u2 = fechas[-1]
#            break
#
#        elif len(row_u1[3].strip()) == 0:
#            fecha_u2 = fechas[-1]
#        elif fechas[0] < row_u1[3]:
#            fecha_u2 = fechas[-1]
#        else:
#            fecha_u2 = row_u1[3]
#        fechas_u.append((fecha_u1, fecha_u2))
#    return fechas_u
#