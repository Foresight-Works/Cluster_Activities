import os
import sys

import networkx as nx

modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
from config import *
from clusters_naming import *

def model_conf_instance(model_name, hyper_params_conf):
    '''
    Build an instance of the model with it's hyperparameters
    :params:
    model_name: The modelling method applied
    hyper_params_conf: A dictionary relating hyperparameters(key) to their values
    :return:
    A model-configuration object ready for training
    '''

    if model_name == 'SpectralClustering': model_conf = SpectralClustering(**hyper_params_conf)
    if model_name == 'AgglomerativeClustering': model_conf = AgglomerativeClustering(**hyper_params_conf)

    return model_conf


def get_clusters(X, names, model_name, hyper_params_conf):
    model_conf = model_conf_instance(model_name, hyper_params_conf)
    print('model_conf', model_conf)
    clustering = model_conf.fit(X)
    clusters_df = pd.DataFrame()
    clusters_df['name'] = names
    clusters_df['cluster'] = clustering.labels_
    clusters_df = clusters_df.sort_values(by=['cluster'], ascending=False)
    # print('distances:', clustering.distances_)
    # print('children:', clustering.children_)
    counts = np.zeros(clustering.children_.shape[0])
    return clustering, clusters_df

def results_file_name(model_name, hyper_params_conf):
    exclude = ['random_state', 'compute_distances']
    for k, v in hyper_params_conf.items():
        if k not in exclude: model_name += '_{k}{v}'.format(k=k, v=str(v).capitalize())
        # name = name[:-1]
    return model_name

# Cluster of Clusters function
def string_similarity_ratio(texts_pair):
    text1, text2 = texts_pair
    return Levenshtein.ratio(text1, text2)

def compare_texts(clusters, text_words_count, threshold, measure='similarity'):
    '''
	Measure texts distances using their string similarity
	:param clusters(dict): The results of a clustering process run, lists of cluster ids and names keyed by the cluster name
	Example
	:param text_words_count(int): The minimun number of words in the texts to compare
	:param threshold: The threshold to determine which texts will be considered similar
	:param measure_type(str): If similarity the results will be filtered for pairs that score higher than the threshold
	'''

    # Filter the input by the number of words in the text
    cluster_keys = list(clusters.keys())
    filter_keys = [c for c in cluster_keys if len(c.replace(' - ', ' ').split(' ')) > text_words_count]
    clusters = {k: v for k, v in clusters.items() if k in filter_keys}
    print('{n} clusters with keys of {t}+ words'.format(n=len(clusters), t=str(text_words_count)))

    # Clusters pair combinations
    cluster_keys = list(clusters.keys())
    clusters_pairs = tuple(combinations(cluster_keys, 2))
    pairs_similarity = {}
    for pair in clusters_pairs:
        pairs_similarity[pair] = string_similarity_ratio(pair)

    # Filter scores by the similarity or distance threshold
    if measure == 'similarity':
        pairs_similarity = {k: v for k, v in pairs_similarity.items() if v >= threshold}
    else:
        pairs_similarity = {k: v for k, v in pairs_similarity.items() if v <= threshold}
    return pairs_similarity

def pairs_to_graph(pairs_similarity):
    keysGraph = nx.Graph()
    Gedges = list(pairs_similarity.keys())
    keysGraph.add_edges_from(Gedges)
    return keysGraph

def is_pair_in_pairs(pair_query, pairs):
	query_in_pairs = None
	pair_query = set(pair_query)
	pairs_sets = [set(pair) for pair in pairs]
	for index, pair_set in enumerate(pairs_sets):
		if pair_query == pair_set:
			query_in_pairs = pairs[index]
			break
	return query_in_pairs


def group_clusters(clusters, threshold=0.9, use_tasks=True):
	'''
	Group clusters
	:parama clusters: The clusters produced keyed by a cluster name and cluster id
	:param threshold: The similarity threshold to pass to the function identifying similar
	clusters
	:parma use_tasks (bool): If true, build the grouped cluster key using the names
	of the tasks in the clusters group, otherwise, use the clusters' names.
	'''

	# Get merged clusters
	grouped_clusters = {}
	pairs_similarity = compare_texts(clusters, 1, threshold)
	keysGraph = pairs_to_graph(pairs_similarity)
	merged_clusters_keys = list(nx.connected_components(keysGraph))
	## Collect the tasks and build a group name for each cluster grouping
	for merged_clusters_index, merged_clusters in enumerate(merged_clusters_keys):
		print('===== Merged clusters keys ======')
		clusters_keys = []
		## Build a grouped cluster name
		# Collect the keys of the clusters merged
		for index, key in enumerate(merged_clusters):
			print(key)
			clusters_keys.append(key)
		# Tasks for the clusters merged
		merged_clusters_tasks = []
		for cluster in merged_clusters:
			# For response dictionary output
			cluster_tasks = [t for t in clusters[cluster]]
			merged_clusters_tasks += cluster_tasks
		print('----- {n} tasks in merged clusters ------'.format(n=len(merged_clusters_tasks)))
		for task in merged_clusters_tasks: print(task[0])
		# Use the task names of cluster keys collected to infer the name for the grouped cluster
		if use_tasks: names_to_use = [task[0] for task in merged_clusters_tasks]
		else: names_to_use = clusters_keys
		merged_cluster_id_clusters_keys = (merged_clusters_index, names_to_use)
		merged_cluster_id, merged_clsuters_key = parts_to_texts(merged_cluster_id_clusters_keys)
		grouped_clusters[(merged_cluster_id, merged_clsuters_key)] = merged_clusters_tasks
		print(30*'-')
		print('Merged cluster key by tasks names  :', merged_clsuters_key)

	return(grouped_clusters)