import sys
import os
import cProfile
pr = cProfile.Profile()
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
extensions = config_vals('data', 'extensions')
ids_col, names_col, task_type = config.get('columns', 'id'),\
                                config.get('columns', 'name'), config.get('columns', 'type')
duration_cols = config_vals('columns', 'duration')
data_cols = [ids_col, names_col, task_type] + duration_cols
model_name = config.get('model', 'name')
language_model_name = config.get('language_models', 'tokens')
affinity = config.get('model', 'affinity')
data_format = config.get('data', 'format')
experiment = '{c}_{p}'.format(c=customer, p=project)
data_dir = config.get('data', 'directory')
db_name = config.get('results', 'database')
table_name = config.get('results', 'table')
n_clusters_percs = config_vals('model', 'n_clusters_perc')
min_cluster_size = int(config.get('model', 'min_cluster_size'))
num_executors = int(config.get('run', 'num_executors'))

# Directories
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'response', data_dir)
results_dir = os.path.join(working_dir, 'results')
matrices_dir = os.path.join(results_dir, 'distance_matrices')
if 'distance_matrices' not in os.listdir(results_dir):
    os.mkdir(matrices_dir)
tokens_path = os.path.join(results_dir, 'tokens.txt')

# App modules
from modules.tokenizers import *
#from modules.clustering import *
#from modules.cluster_names import *
from dev.data.py_postgres import *

# Tables
db_name = 'cluster_activities'
table_name = 'experiments'
conn = psycopg2.connect(database="{db}".format(db=db_name), \
                        user='rony', password='1234', host='localhost', port='5432')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
# tpc = tasks per cluster
metrics_cols = ['tasks_per_cluster_mean', 'tasks_per_cluster_median','wcss', 'bcss', 'ch_index', \
                      'db_index', 'silhouette', 'duration_std']
metrics_optimize = {'min_max_tpc': ('min', 1), 'wcss': ('min', 1), 'bcss': ('max', 1),\
                    'ch_index': ('max', 1), 'db_index': ('min', 1), 'silhouette': ('max', 1)}

results_cols_types = {'run_id': 'numeric', 'files': 'varchar', 'project_name': 'varchar', 'customer': 'varchar', \
                      'num_files': 'numeric', 'run_start': 'timestamp', 'run_end': 'timestamp',\
                      'processes': 'numeric', 'tasks_count': 'numeric', 'language_model': 'varchar',\
                      'clustering_method': 'varchar', 'clustering_params': 'varchar', 'n_clusters_perc': 'numeric',\
                      'num_clusters': 'numeric', 'duration_std': 'numeric',
                      'mean_tpc': 'numeric', 'median_tpc': 'numeric',\
                      'min_tpc': 'numeric', 'max_tpc': 'numeric'}
metrics_cols = list(metrics_optimize.keys())
for col in metrics_cols: results_cols_types[col] = 'numeric'
results_columns, data_types = list(results_cols_types.keys()), list(results_cols_types.values())
