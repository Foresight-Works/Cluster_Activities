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

cur.execute('select result from results where experiment_id = 130;')
# 160: 9 files with cluster keys tuple (cluster number, cluster key)
clustering_result = cur.fetchall()
clustering_result = clustering_result[0][0]
clustering_result = ast.literal_eval(clustering_result)
clusters = clustering_result['clusters']

# Distance Threshold
thresholds = [0, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
thresholds = [0.9]
for threshold in thresholds:
	pairs_similarity = compare_texts(clusters, 3, threshold)
	keysGraph = pairs_to_graph(pairs_similarity)
	merged_clusters_keys = list(nx.connected_components(keysGraph))
	print('merged clusters results')
	result_rows = []
	keys_lists = []
	for merged_clusters in merged_clusters_keys:
		result_rows.append(30 * '=')
		result_rows.append('Keys')
		# Write the keys of the merged clusters
		clusters_keys = []
		for index, key in enumerate(merged_clusters):
			#print('{i}: {k}'.format(i=index, k=key))
			result_rows.append('{i}: {k}'.format(i=index, k=key))
			clusters_keys.append(key)

		CoC_id_clusters_keys = ('1', clusters_keys)
		CoC_id, CoC_key1 = parts_to_texts(CoC_id_clusters_keys)

		# Get Tasks
		result_rows.append('--- Tasks ---')
		merged_clusters_tasks = []
		for cluster in merged_clusters:
			cluster_tasks = [t[1] for t in clusters[cluster]]
			result_rows += cluster_tasks
			merged_clusters_tasks += cluster_tasks
		CoC_id_clusters_keys = ('1', merged_clusters_tasks)
		CoC_id, CoC_key = parts_to_texts(CoC_id_clusters_keys)
		result_rows.append('------------')
		result_rows.append('Merge clusters key by cluster keys: ' + CoC_key1)
		result_rows.append('Merge clusters key by task names  : ' + CoC_key)

	result_rows = '\n'.join(result_rows)
	with open('paired_clusters.txt', 'w') as f: f.write(result_rows)
print('keys_lists=', keys_lists)