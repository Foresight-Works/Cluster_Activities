import psycopg2
import re
import pandas as pd
import pandas.io.sql as sqlio
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
'''
user(str): The Postgres user name
password(str): The Postgres user password  
'''

def create_db(db_name, conn):
    '''
    Create database
    :param db_name(str): The name of the database to connect using the engine
    '''
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE {dn}".format(dn=db_name))
    except psycopg2.errors.DuplicateDatabase as e:
        pass
        #print(e)
        # if "already exists" in str(e):
        #     print(str(e))
        #     decide = input('Drop {dn} (d)?'.format(dn=db_name))
        #     if decide == 'd':
        #         cur.execute("drop database {dn}".format(dn=db_name))
        #         cur.execute("create database {dn}".format(dn=db_name))
    conn.commit()
    cur.close()


def create_table(table_name, cols, cols_types, conn):
    '''
    Create table
    :param user(str): The Postgres user name
    :param password(str): The Postgres user password
    :param db_name(str): The name of the database to connect using the engine
    :param table_name(str): The name of the table to create
    :param cols(list): Table column cluster_key
    :param cols_types: Column response types (postgres)
    '''
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
    cur = conn.cursor()
    # decide = input('Drop and create {tn} table?(y)'.format(tn=table_name))
    decide = 'y'
    if decide == 'y':
        cur.execute("DROP TABLE IF EXISTS {tn}".format(tn=table_name))
        statement_cols_types = ''
        for index, col in enumerate(cols):
            col = col.lower().replace(' ', '_').replace('%', 'perc')
            type = cols_types[index]
            col_type_str = '{c} {t},'.format(c=col, t=type)
            statement_cols_types += col_type_str
        statement_cols_types = statement_cols_types.rstrip(',')
        statement = "CREATE TABLE IF NOT EXISTS {tn} ({ct});".format(tn=table_name, ct=statement_cols_types)
        #print('Create table statement:', statement)
        cur.execute(statement)

    conn.commit()
    cur.close()

def insert_into_table(table_name, cols, cols_vals, conn):
    '''
    Update table
    :param db_name(str): The name of the database to connect using the engine
    :param table_name(str): The name of the table to create
    :param cols(list): Table column cluster_key
    :param cols_vals(list): Column values
    '''
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
    cur = conn.cursor()
    cols_str, vals_str = "(", "("
    for index, col in enumerate(cols):
        val = cols_vals[index]
        cols_str += "'{c}',".format(c=col)
        vals_str += "'{v}',".format(v=val)
    cols_str = cols_str.rstrip(",")+")"
    vals_str = vals_str.rstrip(",")+")"
    print('cols str:', cols_str)
    print('vals str:', vals_str)
    statement = "INSERT INTO {tn} ".format(tn=table_name) + "VALUES " + vals_str
    print('statement:', statement)
    cur.execute(statement)
    conn.commit()
    cur.close()


def update_table(db_name, table_name, cols, cols_vals, conn):
    # TODO: Add condition WHERE
    '''
    Update table
    :param db_name(str): The name of the database to connect using the engine
    :param table_name(str): The name of the table to create
    :param cols(list): Table column cluster_key
    :param cols_vals(list): Column values
    '''
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
    cur = conn.cursor()
    statement = 'UPDATE {tn} SET '.format(tn=table_name)
    for index, col in enumerate(cols):
        val = cols_vals[index]
        set_val = "{c} = '{v}', ".format(c=col, v=val)
        statement += set_val
    statement = statement.rstrip(', ')
    print('statement:', statement)
    cur.execute(statement)
    conn.commit()

def create_db_engine(user, password, db_name):
    '''
    Create database engine
    :param user(str): The Postgres user name
    :param password(str): The Postgres user password
    :param db_name(usr): The name of the database to connect using the engine
    Return: engine such as 'postgresql+psycopg2://postgres:1234@localhost/database'
    '''
    return create_engine('postgresql+psycopg2://{u}:{p}@localhost/{db}'\
                         .format(u=user, p=password, db=db_name)) #:5432

def dfToTable(df, table_name):
    coltypes = df.dtypes
    coltypes = dict(zip(list(coltypes.index), list(coltypes.values)))
    statement_cols_types = '' #id serial PRIMARY KEY, num integer, response varchar
    for col, type in coltypes.items():
        print(col)
        col = col.lower().replace(' ', '_').replace('%', 'perc')
        print(col)
        if type == float:
            type_str = 'numeric'
        elif any(y in col for y in['ID', 'Resource IDs']):
            type_str ='varchar'
        elif any(y in col for y in['Start', 'Finish']):
            type_str ='timestamp'
        elif re.findall('ID', col):
            type_str = 'integer'
        else:
            type_str = 'varchar'
        type_str = '{c} {t},'.format(c=col, t=type_str)
        statement_cols_types += type_str
    statement_cols_types = statement_cols_types.rstrip(',')
    statement = "CREATE TABLE IF NOT EXISTS {tn} ({ct});".format(tn=table_name, ct=statement_cols_types)
    print('create table statement:', statement)
    #cur.execute(statement)
    #conn.commit()



# Connect to database
# try:
#     conn = psycopg2.connect(database="try_db", user="response", password="1234", host="localhost", port="5432")
# except:
#     print("Unable to connect to the database")
# cur = conn.cursor()
#
# # Insert into table
# conn = psycopg2.connect(database="try_db", user="response", password="1234", host="localhost", port="5432")
# cur = conn.cursor()
# cur.execute('INSERT INTO {tn} (id, num, response) VALUES ({c1}, {c2}, {c3})'
#             .format(tn='test', c1=7, c2=5, c3=6))
# conn.commit()
# sql = 'SELECT * FROM {tn}'.format(tn='test')
# dat = sqlio.read_sql_query(sql, conn)
# print(dat)
# cur.close()
# conn.close()