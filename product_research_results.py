import os
import re
import ast
import pandas as pd
import mysql.connector as mysql
import json
from modules.evaluate import *
from modules.config import *

def result_from_table(experiment_id, result_key):
    result_df = pd.read_sql_query("SELECT * FROM results \
    WHERE experiment_id={eid}".format(eid=experiment_id), conn)
    result = result_df[result_key].values[0]
    if result_key == 'result':
	    result = ast.literal_eval(result)['clusters']
    else:
        result = result_df[result_key].values[0]
    return result

def prepare_results(experiment_id):
	# Read metadata
	md_path = os.path.join(os.getcwd(), 'results', 'experiment_{n}'.format(n=str(experiment_id)),\
	                       'parsed_data.xlsx')
	md = pd.read_excel(md_path)
	# print(md.info())
	# print(md['TaskType'].value_counts())
	file_names = [re.findall('file_(.*)\.graphml', n)[0] for n in list(md['File'])]
	md['File'] = file_names
	md['ID_File'] = md['ID']+'_'+md['File']
	md.to_excel('md.xlsx', index=False)
	# Cluster keys per tasks
	results = []
	no_ids = []
	# Read clusters
	#clusters = result_from_table(experiment_id, result_key='result')
	clusters_path = os.path.join(os.getcwd(), 'results', 'experiment_{n}'.format(n=str(experiment_id)), \
	                       'clusters.npy')
	clusters = np.load(clusters_path, allow_pickle=True)[()]
	for key, names in clusters.items():
		cluster_name_id, CoC_name_id = key
		ClusterName = cluster_name_id[1]
		ClusterID = cluster_name_id[0]
		if CoC_name_id[0] == 'not grouped':
			CoCName, CoCID = 'not grouped', 'not grouped'
		else:
			CoCName = CoC_name_id[1]
			CoCID = CoC_name_id[0]
		for name in names:
			# Encoding issue tasks filter
			#if 'Passenger door systems' in name: print(name)
			if type(name) == tuple:
				result = [name[1], name[0], ClusterID, ClusterName, CoCID, CoCName]
				results.append(result)
			else:
				result = [name, ClusterID, ClusterName]
				no_ids.append(result)
	results_df = pd.DataFrame(results, columns=['ID', 'Name', 'ClusterID', 'ClusterName', 'CoCID', 'CoCName'])
	results_df.to_excel('clusters.xlsx'.format(eid=experiment_id), index=False)
	results_df = results_df.drop_duplicates()
	no_ids_df = pd.DataFrame(no_ids, columns=['Name', 'ClusterID', 'ClusterName'])

	a = set(results_df['ID']).intersection(set(md['ID']))
	b = [id for id in results_df['ID'] if id not in md['ID']]
	c = [id for id in md['ID'] if id not in results_df['ID']]
	# Counts
	with_ids = len(results_df)
	no_ids = len(no_ids_df)
	tasks = no_ids + with_ids
	perc_no_ids = round(100 * no_ids/tasks, 1)
	print('tasks clustered=', tasks)
	print('with ids=', with_ids)
	print('no ids= {n}({p})'.format(n=no_ids, p = perc_no_ids))

	if len(no_ids_df)>0:
		no_ids_df.to_excel('no_ids_df.xlsx', index=False)

	## Merge results to metadata
	results_md = pd.merge(md, results_df, on='ID', how='left')
	results_md = results_md[
		['ID', 'File', 'ID_File', 'Name', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart',
		 'ActualEnd', 'Float', 'Status', 'ClusterID', 'ClusterName', 'CoCID', 'CoCName']]
	results_md = results_md.rename(columns={'Name': 'Label'})

	print('results merged to metadata : {n1} rows, {n2} unique IDs'\
		      .format(n1=len(results_md), n2=len(results_md['ID'].unique())))
	vc = results_md['ID'].value_counts()
	duplicates = vc[vc>1]
	print('Duplicate IDs:\n', duplicates)
	results_md_dd = results_md.drop_duplicates()
	print('Duplicate rows dropped from results merged to metadata: {n1} rows, {n2} unique IDs' \
	      .format(n1=len(results_md_dd), n2=len(results_md_dd['ID'].unique())))
	duplicate_ids = duplicates.index
	duplicateIDrows = results_md[results_md['ID'].isin(duplicate_ids)]
	duplicateIDrows.to_excel('duplicateIDrows.xlsx', index=False)

	## Calculate Planned and Actual Duration
	planned_duration = activities_duration_product_research(results_md, 'planned')
	actual_duration = activities_duration_product_research(results_md, 'actual')
	duration_df = pd.merge(planned_duration, actual_duration, on='ID', how='left')
	print('duration results: {n1} rows, {n2} unique IDs'\
		      .format(n1=len(duration_df), n2=len(duration_df['ID'].unique())))

	## Merge results and metadata to duration
	a = set(results_md['ID']).intersection(set(duration_df['ID']))
	b = [id for id in duration_df['ID'] if id not in results_md['ID']]
	c = [id for id in results_md['ID'] if id not in duration_df['ID']]

	results = pd.merge(results_md, duration_df, on='ID')#, how='left')
	#duration_df.to_excel('duration_df.xlsx', index=False)
	print('results/metadata/duration : {n1} rows, {n2} unique IDs'\
		      .format(n1=len(results), n2=len(results['ID'].unique())))

	results = results.rename(columns={'ID': 'Unique_ID'})
	results['ID'] = [i.replace('_'+i.split('_')[-1], '') for i in list(results['Unique_ID'])]
	results = results[['ID', 'Unique_ID', 'TaskType', 'Label', 'PlannedStart', \
	                    'PlannedEnd', 'ActualStart', 'ActualEnd',  'PlannedDuration',  'ActualDuration', \
	                   'Float', 'Status', 'File', 'ClusterID', 'ClusterName', 'CoCID', 'CoCName']]
	return results_md, results
experiment_id = 519
file_name = '3files_fix1'
file_name = file_name.replace('.graphml', '')
results_md, results = prepare_results(experiment_id)
results_md.to_excel('./results/1taskIDsTest/mdClusters{fn}.xlsx'.format(fn=file_name), index=False)
results.to_excel('./results/1taskIDsTest/mdClustersDuration{fn}.xlsx'.format(fn=file_name), index=False)