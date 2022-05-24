import os
import sys
import pandas as pd

modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
#from config import *
from tokens_distances import *
from plots import *
from clustering import *
from clusters_naming import *
results_dir = '/home/rony/Projects_Code/Cluster_Activities/results/cluster_of_clusters_tests'
conn_params = {'host': 'localhost', 'user':'rony', 'password': 'exp8546$fs', 'database': 'CAdb'}
conn = mysql.connect(**conn_params)
cur = conn.cursor()

#cur.execute('select result from results where experiment_id = 130;')
# 160: 9 files with cluster keys tuple (cluster number, cluster key)
#cur.execute('select result from results where experiment_id = 160;')
clustering_result = cur.fetchall()
clustering_result = clustering_result[0][0]
clustering_result = ast.literal_eval(clustering_result)
clusters = clustering_result['clusters']
grouped_clusters = group_clusters(clusters, use_tasks=True)
results_path = os.path.join('grouped_by_tasks.npy')
np.save(results_path, grouped_clusters)
grouped_cluster = np.load(results_path, allow_pickle=True)[()]
