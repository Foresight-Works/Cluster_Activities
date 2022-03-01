import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import pandas.io.sql as sqlio

conn = psycopg2.connect("user=postgres password='1234'")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
cur = conn.cursor()

# Create table
try:
     cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, response varchar);")
except:
     print("Can't create table")
conn.commit()

cur.close()
conn.close()