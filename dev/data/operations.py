import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import pandas.io.sql as sqlio

# Create Database
# con = psycopg2.connect("user=data password='1234'")
# con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
# cursor = con.cursor()
# db_name = "try_db"
# cursor.execute("create database try_db")

# # Create table
# try:
#     cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
# except:
#     print("Can't create table")
# conn.commit()# <--- makes sure the change is shown in the database
# conn.close()
# cur.close()


# Connect to database
try:
    conn = psycopg2.connect(database="try_db", user="data", password="1234", host="localhost", port="5432")
except:
    print("Unable to connect to the database")
cur = conn.cursor()

# Insert into table
conn = psycopg2.connect(database="try_db", user="data", password="1234", host="localhost", port="5432")
cur = conn.cursor()
cur.execute('INSERT INTO {tn} (id, num, data) VALUES ({c1}, {c2}, {c3})'
            .format(tn='test', c1=7, c2=5, c3=6))
conn.commit()
sql = 'SELECT * FROM {tn}'.format(tn='test')
dat = sqlio.read_sql_query(sql, conn)
print(dat)
cur.close()
conn.close()