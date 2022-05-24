import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
#from config import *
from tokens_distances import *
from plots import *

conn_params = {'host': 'localhost', 'user':'rony', 'password': 'exp8546$fs', 'database': 'CAdb'}
conn = mysql.connect(**conn_params)
cur = conn.cursor()

# Cluster of Clusters function
def get_pairs_distances(clusters, ids_vectors):
	'''
	Use clusters' centroids to identify cluster of clusters
	:param clusters(dict): The results of a clustering process run, lists of cluster ids and names keyed by the cluster name
	Example
	:param ids_vectors(dict): The vector for each of the tasks clustered keyed by the task name
	'''

	# Clusters pair combinations
	cluster_keys = list(clusters.keys())
	clusters_pairs = tuple(combinations(cluster_keys, 2))

	# Embedding vectors mean per cluster
	clusters_centroids = {}
	for cluster, ids_names in clusters.items():
		# Cluster vectors
		task_ids = [id_name[0] for id_name in ids_names]
		cluster_vectors = {id: vector for id, vector in ids_vectors.items() if id in task_ids}
		cluster_vectors = np.array(list(cluster_vectors.values()))
		clusters_centroid = np.mean(cluster_vectors, axis=0)
		clusters_centroids[cluster] = clusters_centroid

	centroids = np.stack(list(clusters_centroids.values()))
	distances = pdist(centroids, metric='euclidean')
	distances_s = pd.Series(distances)
	print(distances_s.describe().apply(lambda x: format(x, 'f')))
	histogram_stats(distances, 'Clusters Distances Distribution', 'Distance', './results/cluster_distances_hist.png')

	clusters_pairs = list(combinations(cluster_keys, 2))
	pairs_distances = dict(zip(clusters_pairs, distances))
	return pairs_distances



ids_vectors = np.load('./results/ids_embeddings.npy', allow_pickle=True)[()]
# 9 files
cur.execute('select result from results where experiment_id = 130;')
clustering_result = cur.fetchall()
clustering_result = clustering_result[0][0]
clustering_result = ast.literal_eval(clustering_result)
clusters = clustering_result['clusters']

## Filters
# Words in key
cluster_keys = list(clusters.keys())
filter_keys = [c for c in cluster_keys if len(c.replace(' - ', ' ').split(' ')) > 3]
filtered_cluster = {k: v for k, v in clusters.items() if k in filter_keys}
print('{n} clusters with keys of 3+ words'.format(n=len(filtered_cluster)))
pairs_distances = get_pairs_distances(filtered_cluster, ids_vectors)

# Distance Threshold
distance_threshold = 0.8
filtered_pairs_distances = {k: v for k, v in pairs_distances.items() if v >= distance_threshold}
filtered_pairs_keys = list(filtered_pairs_distances.keys())
result_rows = []
for pair_keys in filtered_pairs_keys:
	result_rows.append(30 * '=')
	result_rows.append('Keys: {k1} | {k2}'.format(k1=pair_keys[0], k2=pair_keys[1]))
	tasks = []
	for key in pair_keys:
		for task in clusters[key]:
			a = task[1]
			result_rows.append(task[1])
result_rows = '\n'.join(result_rows)
with open('results/distance_threshold_tests/paired_clusters1.txt', 'w') as f: f.write(result_rows)
