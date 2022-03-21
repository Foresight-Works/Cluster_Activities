import mysql.connector as mysql
from setup import *
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs'}
conn = mysql.connect(**conn_params)
c = conn.cursor()
db_name = 'CAdb'
#Database and Tables
print('connected')
c = conn.cursor()
statement = "CREATE DATABASE IF NOT EXISTS {db}".format(db=db_name)
print(statement)
c.execute(statement)
conn_params['database'] = db_name
print('conn_params:', conn_params)
conn = mysql.connect(**conn_params)
c = conn.cursor()
#c.execute('DROP TABLE IF EXISTS runs')
#c.execute('DROP TABLE IF EXISTS results')
create_table_statement = build_create_table_statement('{db}.runs'.format(db=db_name), runs_cols, runs_types)
c.execute(create_table_statement)
create_table_statement = build_create_table_statement('{db}.results'.format(db=db_name), results_cols, results_types)
c.execute(create_table_statement)
print('checked/created tables')