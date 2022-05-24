from itertools import combinations
import matplotlib.pyplot as plt
import networkx as nx

# Visualize
def draw_graph(G):
	'''
	Extension to networkx/matplotlib graph drawing function, adding node names and visual properties
	:param G: Graph object
	:show: A graph plot that can be saved
	'''
	pos = nx.spring_layout(G)
	nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size=500)
	nx.draw_networkx_labels(G, pos)
	nx.draw_networkx_edges(G, pos, edge_color='r')
	nx.draw_networkx_edges(G, pos)
	plt.show()

def pairs_to_graph(pairs_similarity):
    keysGraph = nx.Graph()
    Gedges = list(pairs_similarity.keys())
    keysGraph.add_edges_from(Gedges)
    return keysGraph

def get_edge_weight(weights_dictionary, Gedge):
	weights_dictionary_keys_sets = [set(pair) for pair in list(weights_dictionary.keys())]
	Gedge_set = set(Gedge)
	Gedge_weight = None
	for pair_set in weights_dictionary_keys_sets:
		if Gedge_set == pair_set:
			try:
				Gedge_weight = pairs_similarity[Gedge]
			except KeyError:
				Gedge_reversed = (Gedge[1], Gedge[0])
				Gedge_weight = pairs_similarity[Gedge_reversed]
			break
	return Gedge_weight

def is_pair_in_pairs(pair_query, pairs):
	query_in_pairs = None
	pair_query = set(pair_query)
	pairs_sets = [set(pair) for pair in pairs]
	for index, pair_set in enumerate(pairs_sets):
		if pair_query == pair_set:
			query_in_pairs = pairs[index]
			break
	return query_in_pairs

pairs_similarity = {('a', 'b'):0.1, ('b', 'c'):0.2, ('c', 'k'):0.4, ('e', 'f'):0.3, ('f', 'g'):0.4}
keysGraph = pairs_to_graph(pairs_similarity)
merged_clusters_keys = list(nx.connected_components(keysGraph))
print('merged_clusters_keys:', merged_clusters_keys)
merged_clusters_graphs = [keysGraph.subgraph(c).copy() for c in nx.connected_components(keysGraph)]
print('merged_clusters_graphs:', merged_clusters_graphs)

# Get edge weights for each weight in each connected graph
for graph in merged_clusters_graphs:
	Gedges = graph.edges()
	print('Gedges:', Gedges)
	for Gedge in Gedges:
		Gedge_weight = get_edge_weight(pairs_similarity, Gedge)
		print(Gedge, Gedge_weight)
		pair_key = is_pair_in_pairs(Gedge, list(pairs_similarity.keys()))
		print(Gedge, 'in pairs is', pair_key)


#draw_graph(keysGraph)