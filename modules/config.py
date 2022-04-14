# Data and Matrices Storage
import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)

import boto3
ds_bucket = 'foresight-ds-docs'
aws_access_key_id = 'AKIAQIALQA3XKOG2MNFS'
aws_secret_access_key = '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'
s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
ds_bucket_obj = s3.Bucket(ds_bucket)
matrices_dir = 'matrices'
extensions = ['graphml', 'csv', 'xer', 'zip']
ids_col, names_col, task_type = 'ID', 'Label', 'TaskType'
duration_cols = ['PlannedStart', 'PlannedEnd']
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']

## Models
# Cluster analysis
clustering_model_name = 'AgglomerativeClustering'
affinity = 'euclidean'
n_clusters_percs = [2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20]
min_cluster_size = 0
# Language
sentences_model = 'all-MiniLM-L6-v2'
tokens_model = 'glove-twitter-25'
# Run
num_executors = 6
# Database
db_name = 'CAdb'
location_db_params = {'Local': {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': db_name},\
                      'Remote': {'host': '172.31.36.11', 'user':'researchUIuser', 'password':'query1234$fs', 'database': db_name}}
# Tables
metrics_optimize = {'min_max_tpc': ('min', 1), 'wcss': ('min', 1), 'bcss': ('max', 1), 'ch_index': ('max', 1),\
'db_index':('min', 1), 'silhouette':('max', 1), 'words_pairs': ('max', 1)}
metrics_cols = {col: 'TEXT' for col, v in metrics_optimize.items()}
cols_types = {'experiment_id': 'TEXT', 'run_id': 'TEXT', 'file_name': 'TEXT',\
                      'num_files': 'TEXT', 'run_start': 'TEXT', 'run_end': 'TEXT', 'duration':'TEXT',\
                      'tasks_count': 'TEXT', 'language_model': 'TEXT', 'clustering_method': 'TEXT', 'clustering_params': 'TEXT',\
                      'num_clusters': 'TEXT', 'mean_duration_std':'TEXT',\
                      'tasks_per_cluster_mean': 'TEXT', 'tasks_per_cluster_median': 'TEXT',\
                      'min_tasks_per_cluster': 'TEXT', 'max_tasks_per_cluster': 'TEXT'}
cols_types = {**cols_types, **metrics_cols}
runs_cols, runs_types = list(cols_types.keys()), list(cols_types.values())
results_cols_types = {**cols_types, **metrics_cols, 'Result': 'JSON'}
results_cols, results_types = list(results_cols_types.keys()), list(results_cols_types.values())
metrics_cols = list(metrics_cols.keys())
# Paths and Directories
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data', 'experiments')
results_dir = os.path.join(working_dir, 'results')
tokens_path = os.path.join(results_dir, 'tokens.txt')
models_dir = os.path.join(working_dir, 'models')
standard_dirs = ['results', 'models', 'matrices', 'tmp']
for dir in standard_dirs:
    if dir not in os.listdir('.'):
        os.mkdir(dir)