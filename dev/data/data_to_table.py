import pandas as pd
import os
from modules.py_postgres import *
#
data_files = ['CCGT D1.csv', 'CCGT D2.csv', 'DUKE S2X1CC_2013_10_27.csv', 'DUKE WAYNE COUNTY_2012-01-29.csv']
data_path = './data/raw_data/'
projects_df = pd.DataFrame()
for file in data_files:
    project_df = pd.read_csv(os.path.join(data_path, '{f}'.format(f=file)))
    projects_df = project_df.append(project_df)
print(projects_df.info())

engine = create_db('ccgt')
#dfToTable(projects_df, 'projects')
projects_df.to_sql('projects', engine)
dat = sqlio.read_sql_query('SELECT * FROM projects', engine)
print(dat.head())

