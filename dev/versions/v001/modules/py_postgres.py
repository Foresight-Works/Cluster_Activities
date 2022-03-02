import psycopg2
import re
import pandas as pd
import pandas.io.sql as sqlio
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
conn = psycopg2.connect("user=postgres password='1234'")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
cur = conn.cursor()


def create_db(db_name):
    #a = cur.execute("SELECT FROM pg_database WHERE datname = {db}".format(db=db_name))
    #print(a)

    try:
        cur.execute("create database {dn}".format(dn=db_name))
    except psycopg2.errors.DuplicateDatabase as e:
        if "already exists" in str(e):
            print(str(e))
            decide = input('Drop {dn} (d)?'.format(dn=db_name))
            if decide == 'd':
                cur.execute("drop database {dn}".format(dn=db_name))
            new_db = input('Create new database (database name)?').rstrip().lstrip()
            if new_db:
                cur.execute("create database {dn}".format(dn=new_db))
    engine = create_engine('postgresql+psycopg2://postgres:1234@localhost/{db}'.format(db=db_name)) #:5432
    return engine

def dfToTable(df, table_name):
    coltypes = df.dtypes
    coltypes = dict(zip(list(coltypes.index), list(coltypes.values)))
    command_cols_types = '' #id serial PRIMARY KEY, num integer, data varchar
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
        command_cols_types += type_str
    command_cols_types = command_cols_types.rstrip(',')
    command = "CREATE TABLE IF NOT EXISTS {tn} ({ct});".format(tn=table_name, ct=command_cols_types)
    print('create table command:', command)
    cur.execute(command)
    conn.commit()



#def create_table(table_name, columns_types):

# try:
#     cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
# except:
#     print("Can't create table")
# conn.commit()# <--- makes sure the change is shown in the database
# conn.close()
# cur.close()


# Connect to database
# try:
#     conn = psycopg2.connect(database="try_db", user="data", password="1234", host="localhost", port="5432")
# except:
#     print("Unable to connect to the database")
# cur = conn.cursor()
#
# # Insert into table
# conn = psycopg2.connect(database="try_db", user="data", password="1234", host="localhost", port="5432")
# cur = conn.cursor()
# cur.execute('INSERT INTO {tn} (id, num, data) VALUES ({c1}, {c2}, {c3})'
#             .format(tn='test', c1=7, c2=5, c3=6))
# conn.commit()
# sql = 'SELECT * FROM {tn}'.format(tn='test')
# dat = sqlio.read_sql_query(sql, conn)
# print(dat)
# cur.close()
# conn.close()