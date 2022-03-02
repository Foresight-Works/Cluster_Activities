import sys
import os
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
#nltk.download('stopwords')

from configparser import ConfigParser
def config_vals(header, param):
    vals = config.get(header, param)
    return [i.lstrip().rstrip() for i in vals.split(',')]

# Configuration
config = ConfigParser()
config.read(r'./config.ini')
customer = config.get('project', 'customer')
project = config.get('project', 'name')
file = config.get('data', 'file')
extensions = config_vals('data', 'extensions')
ids_col, names_col, task_type = config.get('columns', 'id'),\
                                config.get('columns', 'name'), config.get('columns', 'type')
duration_cols = config_vals('columns', 'duration')
data_cols = [ids_col, names_col, task_type] + duration_cols
model_name = config.get('model', 'name')
n_clusters_perc = config_vals('model', 'n_clusters_perc')
affinity = config.get('model', 'affinity')
data_format = config.get('data', 'format')
experiment = '{c}_{p}_{f}'.format(c=customer, p=project, f=file.replace('.zip', ''))
db_name = config.get('results', 'database')
table_name = config.get('results', 'table')
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data', 'experiments')
data_path = os.path.join(data_dir, file)
results = os.path.join(working_dir, 'results')
results_dir = os.path.join(results, experiment)
if experiment not in results_dir:
    os.mkdir(results_dir)
tokens_path = os.path.join(results_dir, 'tokens.txt')

# App odules
from modules.tokenizers import *

# Tables
db_name = 'cluster_activities'
table_name = 'experiments'
conn = psycopg2.connect(database="{db}".format(db=db_name), \
                        user='rony', password='1234', host='localhost', port='5432')
metrics_optimize = {'min_max_tpc': ('min', 1), 'wcss': ('min', 1), 'bcss': ('max', 1), 'ch_index': ('max', 1),\
'db_index':('min', 1), 'silhouette':('max', 1), 'words_pairs': ('max', 1)}
metrics_cols = {col:'numeric' for col, v in metrics_optimize.items()}
print('metrics_cols:', metrics_cols)
results_cols_types = {'run_id': 'varchar', 'file_name': 'varchar', 'project_name': 'varchar', 'customer': 'varchar', \
                      'num_files': 'numeric', 'run_start': 'timestamp', 'run_end': 'timestamp', 'duration':'numeric',\
                      'tasks_count': 'numeric', 'language_model': 'varchar', 'clustering_method': 'varchar', 'clustering_params': 'varchar',\
                      'n_clusters_perc': 'numeric', 'num_clusters': 'numeric', 'mean_duration_std':'numeric',\
                      'tasks_per_cluster_mean': 'numeric', 'tasks_per_cluster_median': 'numeric',\
                      'min_tasks_per_cluster': 'numeric', 'max_tasks_per_cluster': 'numeric'}
results_cols_types = {**results_cols_types, **metrics_cols}
print('results_cols_types:', results_cols_types)
print('{n} result table columns'.format(n=len(results_cols_types)))
results_columns, data_types = list(results_cols_types.keys()), list(results_cols_types.values())


