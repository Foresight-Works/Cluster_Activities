import os
import numpy as np
import pandas as pd
experiment_id = 511
# Metadata Task IDS
md_path = os.path.join(os.getcwd(), 'results', 'experiment_{n}'.format(n=str(experiment_id)),\
	                       'parsed_data.xlsx')
md = pd.read_excel(md_path)
md_tasks_ids = list(md['ID'])
#Clusters Task IDs
# results/experiment_510/runs/5/references/clustering_result.npy
clusters_path = os.path.join(os.getcwd(), 'results', 'experiment_{n}'.format(n=str(experiment_id)),\
	                       'runs/1/references/clustering_result.npy')

#/home/rony/Projects_Code/Cluster_Activities/results/experiment_511/clusters.npy
clusters_path = os.path.join(os.getcwd(), 'results', 'experiment_{n}'.format(n=str(experiment_id)),\
	                       'clusters.npy')
clusters = np.load(clusters_path, allow_pickle=True)[()]
clusters_tasks_ids = []
for key, tasks_tuples in clusters.items():
	clusters_tasks_ids += [tt[1] for tt in tasks_tuples]
a = set(md_tasks_ids).difference(set(clusters_tasks_ids))
z=1
# b = [id for id in duration_df['ID'] if id not in results_md['ID']]
# c = [id for id in results_md['ID'] if id not in duration_df['ID']]

