import sqlite3
import pandas as pd
from setup import *
conn = sqlite3.connect('CAdb')
c = conn.cursor()
# c.execute("Drop table if exists experiments ")
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(c.fetchall())

c.execute("SELECT experiment_id FROM experiments")
print(c.fetchall())
experiment_ids = pd.read_sql_query("SELECT experiment_id from experiments", conn).astype(int)
recent_id = int(max(experiment_ids.values)[0])
print(recent_id, type(recent_id))
