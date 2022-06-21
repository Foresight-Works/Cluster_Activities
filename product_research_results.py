import os
import re
import ast
import pandas as pd
import mysql.connector as mysql
from modules.evaluate import *

service_location = 'Local'
db_name = 'CAdb'
location_db_params = {'Local': {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': db_name},\
                      'Remote': {'host': '172.31.36.11', 'user':'researchUIuser', 'password':'query1234$fs', 'database': db_name}}
conn_params = location_db_params[service_location]
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

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
	md_path = os.path.join(os.getcwd(),'results','experiment_{n}'.format(n=str(experiment_id)),\
	                       'parsed_data.xlsx')
	md = pd.read_excel(md_path)
	# Unique task ids by source file
	file_names = [re.findall('file_(.*)\.graphml', n)[0] for n in list(md['File'])]
	md['File'] = file_names
	md['ID'] = md['ID']+'_'+md['File']
	# Cluster keys per tasks
	results = []
	no_ids = []
	clusters = result_from_table(experiment_id, result_key='result')
	file_name = result_from_table(experiment_id, result_key='file_name')
	file_name = re.findall('file_(.*)\.graphml', file_name)[0]
	for key, names in clusters.items():
		key_tuple = ast.literal_eval(key)
		ClusterName = key_tuple[1]
		ClusterID = '{ck}_{fn}'.format(ck=key_tuple[0], fn=file_name)
		for name in names:
			# Encoding issue tasks filter
			#if 'Passenger door systems' in name: print(name)
			if type(name) == list:
				result = ['{n1}_{n2}'.format(n1=name[1], n2=file_name), name[0], ClusterID, ClusterName]
				results.append(result)
			else:
				result = [name, ClusterID, ClusterName]
				no_ids.append(result)
	results_df = pd.DataFrame(results, columns=['ID', 'Name', 'ClusterID', 'ClusterName'])
	no_ids_df = pd.DataFrame(no_ids, columns=['Name', 'ClusterID', 'ClusterName'])

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
	results_md = pd.merge(results_df, md, on='ID')
	print('results merged to metadata : {n1} rows, {n2} unique IDs'\
		      .format(n1=len(results_md), n2=len(results_md['ID'].unique())))

	## Calculate Planned and Actual Duration
	planned_duration = activities_duration_product_research(results_md, 'planned')
	actual_duration = activities_duration_product_research(results_md, 'actual')
	duration_df = pd.merge(planned_duration, actual_duration)
	print('duration results: {n1} rows, {n2} unique IDs'\
		      .format(n1=len(duration_df), n2=len(duration_df['ID'].unique())))

	## Merge results and metadata to duration
	results = pd.merge(results_md, duration_df, on='ID', how='left')
	print('results/metadata/duration : {n1} rows, {n2} unique IDs'\
		      .format(n1=len(results), n2=len(results['ID'].unique())))

	results = results.rename(columns={'ID': 'Unique_ID'})
	results['ID'] = [i.replace('_'+i.split('_')[-1], '') for i in list(results['Unique_ID'])]
	results = results[['ID', 'Unique_ID', 'TaskType', 'Label', 'PlannedStart', \
	                    'PlannedEnd', 'ActualStart', 'ActualEnd',  'PlannedDuration',  'ActualDuration', \
	                   'Float', 'Status', 'File', 'ClusterID', 'ClusterName']]
	return results

experiment_id = 426
results = prepare_results(experiment_id)
results.to_excel('product_research_results.xlsx', index=False)
