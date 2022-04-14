from config import *
import mysql.connector as mysql

def build_create_table_statement(table_name, cols, cols_types):
    '''
    Build Create table statement with the cluster_key and types for each column
    :param table_name(str): The name of the table to create
    :param cols(list): Table column cluster_key
    :param cols_types: Column response types (postgres)
    '''
    statement_cols_types = ''
    for index, col in enumerate(cols):
        col = col.lower().replace(' ', '_').replace('%', 'perc')
        type = cols_types[index]
        col_type_str = '{c} {t},'.format(c=col, t=type)
        statement_cols_types += col_type_str
    statement_cols_types = statement_cols_types.rstrip(',')
    return "CREATE TABLE IF NOT EXISTS {tn} ({ct});".format(tn=table_name, ct=statement_cols_types)

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
c.execute('DROP TABLE IF EXISTS experiments')
c.execute('DROP TABLE IF EXISTS runs')
c.execute('DROP TABLE IF EXISTS results')
create_table_statement = build_create_table_statement('{db}.runs'.format(db=db_name), runs_cols, runs_types)
c.execute(create_table_statement)
create_table_statement = build_create_table_statement('{db}.results'.format(db=db_name), results_cols, results_types)
c.execute(create_table_statement)
c.execute('create table if not exists experiments (experiment_id TEXT)')
print('checked/created tables')