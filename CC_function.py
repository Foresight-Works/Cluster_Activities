import os
import sys
import time

modules_dir = os.path.join(os.getcwd(), 'modules')
print('modules_dir:', modules_dir)
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

import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
print('modules_dir:', modules_dir)
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
#from config import *
from tokens_distances import *
from plots import *
from clustering import *
from clusters_naming import *
from utils import write_duration
results_dir = '/home/rony/Projects_Code/Cluster_Activities/results/cluster_of_clusters_tests'
conn_params = {'host': 'localhost', 'user':'rony', 'password': 'exp8546$fs', 'database': 'CAdb'}
conn = mysql.connect(**conn_params)
cur = conn.cursor()
experiment_id = 269
cur.execute('select result from results where experiment_id = {eid};'.format(eid=str(experiment_id)))
clustering_result = cur.fetchall()
clustering_result = clustering_result[0][0]
clustering_result = ast.literal_eval(clustering_result)
clusters = clustering_result['clusters']
start = time.time()
grouped_clusters = group_clusters(clusters, threshold=0.9)
results_path = os.path.join('dev/clusters_or_clusters/key_similarity/grouped_by_tasks.npy')
write_duration('grouping clusters', start)