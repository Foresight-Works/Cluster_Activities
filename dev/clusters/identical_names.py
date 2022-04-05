import ast
import os
import re
import nltk
import itertools
from itertools import combinations
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import mysql.connector as mysql
from collections import defaultdict
import string

db_name = 'CAdb'
location_db_params = {'Local': {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': db_name},\
                      'Remote': {'host': '172.31.36.11', 'user':'researchUIuser', 'password':'query1234$fs', 'database': db_name}}
conn_params = location_db_params['Local']
conn = mysql.connect(**conn_params)
cur = conn.cursor()
cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
experiment_id = 138
def result_from_table(experiment_id, result_key='clusters'):
    result_df = pd.read_sql_query("SELECT * FROM results \
    WHERE experiment_id={eid}".format(eid=experiment_id), conn)
    result = result_df['result'].values[0]
    result = ast.literal_eval(result)
    if result_key == 'clusters':
        result_key = [c for c in result.keys() if 'duration' not in c][0]
    result = result[result_key]
    clusters = {}
    for k, v in result.items():
        if len(k.split(' ')) > 1:
            v = [i[1] for i in v]
            clusters[k] = v
    return clusters

clusters = result_from_table(experiment_id)
for key, names in clusters.items():
    if len(set(names))==1:
        print(30*'-')
        print(key)
        print(names)

    #print(len(set(names)))
    #for name in names:



