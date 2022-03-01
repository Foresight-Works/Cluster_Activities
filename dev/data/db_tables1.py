import pandas as pd
import os
from modules.py_postgres import *
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)
user = 'rony'
password = '1234'

# Database
db_name = 'cluster_activities'
create_db(db_name)

# Experiments table
table_name = 'experiments'
columns_types = {'file_name': 'varchar', 'project_name': 'varchar', 'customer': 'varchar',\
                 'run_start': 'timestamp', 'run_end': 'timestamp', 'processes': 'numeric',\
                 'tasks_count': 'numeric', 'n_clusters_perc': 'numeric',\
                 'num_clusters': 'numeric', 'tasks_per_cluster_mean': 'numeric',\
                 'tasks_per_cluster_median': 'numeric', 'wcss_score': 'numeric', 'duration_std_score': 'numeric'}
columns = ['file_name', 'project_name', 'customer', 'run_start', 'run_end', 'processes', 'tasks_count',\
        'n_clusters_perc', 'num_clusters', 'tasks_per_cluster_mean', 'tasks_per_cluster_median',\
        'wcss_score', 'duration_std_score']
data_types = ['varchar', 'varchar', 'varchar', 'timestamp', 'timestamp',\
             'numeric', 'numeric', 'numeric', 'numeric', 'numeric', 'numeric', 'numeric', 'numeric']
print('columns_types:', columns, data_types)
create_table(db_name, table_name, columns, data_types)
col_values = ['file1', 'project1', 'customer1', dt_string, dt_string,\
              8, 9, 9, 9, 9, 9, 9, 9]
insert_into_table(db_name, table_name, columns, col_values)

conn = psycopg2.connect(database="{db}".format(db=db_name), \
                            user='rony', password='1234', host='localhost', port='5432')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
cur = conn.cursor()
print('Table values')
cur.execute("SELECT * FROM {tn}".format(tn=table_name))
print(cur.fetchall())
sql = "SELECT * FROM {tn}".format(tn=table_name)
dat = sqlio.read_sql_query(sql, conn)
print(dat.T)

conn.close()
cur.close()
    # print(type(df))
    # print(df)

# data_files = ['CCGT D1.csv', 'CCGT D2.csv', 'DUKE S2X1CC_2013_10_27.csv', 'DUKE WAYNE COUNTY_2012-01-29.csv']
# data_path = '../../response/raw_data/'
# projects_df = pd.DataFrame()
# for file in data_files:
#     project_df = pd.read_csv(os.path.join(data_path, '{f}'.format(f=file)))
#     projects_df = project_df.append(project_df)
# print(projects_df.info())
#
# engine = create_db('ccgt')
# #dfToTable(projects_df, 'projects')
# projects_df.to_sql('projects', engine)
# dat = sqlio.read_sql_query('SELECT * FROM projects', engine)
# print(dat.head())

