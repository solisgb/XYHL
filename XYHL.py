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

    db = eval(project.find('db').text)
    con = pyodbc.connect(db_con_str.con_str(db))
    cur = con.cursor()
    cur.execute(project.find('select_master'))

    con.close()

