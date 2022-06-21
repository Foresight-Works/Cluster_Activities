import numpy as np
import ast
import os
import pandas as pd

files = os.listdir()
#print(files)
file = 'clusters.npy'
r = np.load(file, allow_pickle=True)[()]
for k,v in r.items(): print(k,v)
qin = 'Vehicle 003 - Validation Vehicle Functions ; EMC pre-test'
qout ='Vehicle 001 - FO2 WS6 WT1 (inc Modulprufung)'
queries = {'qin':qin, 'qout':qout}
# file_path = '/home/rony/Projects_Code/Cluster_Activities/clustering_result.txt'
# r = open(file_path).read()
# for k in list(r.keys()): print(k[1])
# print(30*'-')
# no_ids = pd.read_excel('/home/rony/Projects_Code/Cluster_Activities/no_ids_df.xlsx')
# for k in list(no_ids['ClusterName'].unique()): print(k)
# a = set(list([k[1] for k in r.keys()]))
# b = set(list(no_ids['ClusterName']))
# print(a,b)
# print('difference:', a.difference((b)))
#r = ast.literal_eval(r)['clusters']
clusters_names = list(r.values())
for cluster_names in clusters_names:
	for name in cluster_names:
		for qname, query in queries.items():
			if query in name:
				print(qname, ':', query)
				print('Result:', name)