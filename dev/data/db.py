import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
conn = psycopg2.connect("user=response password='1234'")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
cur = conn.cursor()


# Create Database
db_name = 'CCGT'
cur.execute("create database {dn}".format(dn=db_name))
conn.close()
cur.close()
