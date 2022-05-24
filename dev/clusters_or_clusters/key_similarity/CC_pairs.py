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
results_dir = '/home/rony/Projects_Code/Cluster_Activities/results/cluster_of_clusters_tests'
conn_params = {'host': 'localhost', 'user':'rony', 'password': 'exp8546$fs', 'database': 'CAdb'}
conn = mysql.connect(**conn_params)
cur = conn.cursor()

ids_vectors = np.load('/home/rony/Projects_Code/Cluster_Activities/results/ids_embeddings.npy', allow_pickle=True)[()]
cur.execute('select result from results where experiment_id = 130;')
clustering_result = cur.fetchall()
clustering_result = clustering_result[0][0]
clustering_result = ast.literal_eval(clustering_result)
clusters = clustering_result['clusters']

# Distance Threshold
thresholds = [0, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9]
thresholds = [0.9]
summary =[]
for threshold in thresholds:
	pairs_similarity = compare_texts(clusters, 3, threshold)
	pairs = list(pairs_similarity.keys())
	first_pair = pairs[0]
	print('first_pair:', first_pair, type(first_pair))
	print(pairs_similarity)

	# Get descriptive statistics and distribution for distances/similarity values
	if threshold == 0:
		distances = np.array(list(pairs_similarity.values()))
		distances_s = pd.Series(distances)
		print(distances_s.describe().apply(lambda x: format(x, 'f')))
		histogram_stats(distances, 'String Similarity Distribution', 'Similarity',\
		                os.path.join(results_dir, 'cluster_similarity_hist.png'))

	# Count the number of clustered that were found similar
	pairs = list(pairs_similarity.keys())
	pairs_keys = []
	for pair in pairs:
		pairs_keys += list(pair)
	num_clusters = len(set(pairs_keys))

	mean_similarity = float(np.mean(np.array(list(pairs_similarity.values()))))
	median_similarity = float(np.median(np.array(list(pairs_similarity.values()))))
	mean_similarity, median_similarity = round(mean_similarity, 2), round(median_similarity, 2)
	summary.append([threshold, num_clusters, mean_similarity, median_similarity])
	result_rows = []
	for pair_keys in list(pairs_similarity.keys()):
		result_rows.append(30 * '=')
		result_rows.append('Keys')
		result_rows.append('1: {k1} | 2: {k2}'.format(k1=pair_keys[0], k2=pair_keys[1]))
		result_rows.append('--- Tasks ---')
		tasks = []
		for index, key in enumerate(pair_keys):
			for task in clusters[key]:
				result_rows.append('{t} ({i})'.format(t=task[1], i=str(index+1)))
	result_rows = '\n'.join(result_rows)
	with open(os.path.join(results_dir, 'paired_clusters_{t}.txt'\
			.format(t=str(threshold).replace('.', ''))), 'w') as f: f.write(result_rows)
summary_cols = ['threshold', 'clusters count', 'mean similarity', 'median similarity']
summmary_df = pd.DataFrame(summary, columns=summary_cols)
summmary_df.to_excel(os.path.join(results_dir, 'summary.xlsx'), index=False)