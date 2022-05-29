import networkx as nx
from modules.libraries import *
from modules.config import *
from modules.clusters_naming import *
from clusters_naming import *
from modules.tokenizers import normalize_texts

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

def get_clusters_keys(clusters, text_words_count=1):
	'''
	Get the keys of the clusters from a clustering results
	Filter the input by the number of words in the text
	:param clusters(dict): The results of a clustering process run, lists of cluster ids and names keyed by the cluster name
	:param text_words_count(int): The minimun number of words in the texts to compare
	'''
	cluster_keys = list(clusters.keys())
	filter_keys = [c for c in cluster_keys if len(c.replace(' - ', ' ').split(' ')) > text_words_count]
	clusters = {k: v for k, v in clusters.items() if k in filter_keys}
	cluster_keys = list(clusters.keys())
	print('{n} clusters with keys of {t}+ words'.format(n=len(clusters), t=str(text_words_count)))
	return cluster_keys

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

def compare_texts(texts, text_words_count, threshold, measure='similarity'):
	'''
	Measure texts distances using their string similarity
	:param threshold: The threshold to determine which texts will be considered similar
	:param measure_type(str): If similarity the results will be filtered for pairs that score higher than the threshold
	'''
	texts_pairs = tuple(combinations(texts, 2))
	pairs_similarity = {}
	for pair in texts_pairs:
		pairs_similarity[pair] = string_similarity_ratio(pair)
	# Filter scores by the similarity or distance threshold
	if measure == 'similarity':
		pairs_similarity = {k: v for k, v in pairs_similarity.items() if v >= threshold}
	else:
		pairs_similarity = {k: v for k, v in pairs_similarity.items() if v <= threshold}
	return pairs_similarity

def group_clusters(cluster_keys, threshold=0.9):
	'''
	Group clusters by their keys using a string similarity method
	:param clusters: The clusters to group
	'''
	# Get merged clusters
	pairs_similarity = compare_texts(cluster_keys, 1, threshold)
	keysGraph = pairs_to_graph(pairs_similarity)
	merged_clusters_keys = list(nx.connected_components(keysGraph))
	return merged_clusters_keys

def names_for_keys(clusters, clusters_keys):
    '''
    Collect the keys or the task names for the clusters merged
    :param clusters(dict): Cluster built and stored under clustering_result['clusters']
    :param clusters_keys(list): Keys of clusters whose activity names are collected
    '''
    clusters_keys = list(clusters_keys)
    clusters_tasks = []
    # Tasks per cluster
    for cluster_key in clusters_keys:
	    cluster_tasks = clusters[cluster_key]
	    cluster_tasks = [t[0] for t in cluster_tasks]
	    clusters_tasks += cluster_tasks
    return clusters_tasks