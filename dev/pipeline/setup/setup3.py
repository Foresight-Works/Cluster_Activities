import sys
import os
import shutil
from datetime import datetime
from difflib import SequenceMatcher
import re
import json
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import silhouette_score
from sklearn.cluster import SpectralClustering, AgglomerativeClustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram

from pathlib import Path
from flask import Flask
from flask import Response, jsonify, request, redirect, url_for, send_from_directory
import socket
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer, util
from zipfile import ZipFile
from configparser import ConfigParser

def config_vals(header, param):
    vals = config.get(header, param)
    return [i.lstrip().rstrip() for i in vals.split(',')]

# Configuration
config = ConfigParser()
config.read(r'./config.ini')
customer = config.get('project', 'customer')
project = config.get('project', 'name')
file = config.get('response', 'file')
extensions = config_vals('response', 'extensions')
ids_col, names_col, task_type = config.get('columns', 'id'),\
                                config.get('columns', 'name'), config.get('columns', 'type')
duration_cols = config_vals('columns', 'processes')
data_cols = [ids_col, names_col, task_type] + duration_cols
model_name = config.get('model', 'name')
n_clusters_perc = int(config.get('model', 'n_clusters_perc'))
eval_metrics = config_vals('model', 'eval_metrics')
affinity = config.get('model', 'affinity')
data_format = config.get('response', 'format')
experiment = '{c}_{p}_{f}'.format(c=customer, p=project, f=file.replace('.zip', ''))

# Directories
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, '../../../modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, '../../../data', project)
results_dir = os.path.join(working_dir, '../../../results', experiment)
if experiment in os.listdir('../../../results'):
    shutil.rmtree(results_dir)
os.mkdir(results_dir)
with open(os.path.join(results_dir, 'tokens.txt'), 'w') as f: f.write(' ')

# Paths
data_path = os.path.join(data_dir, file)

# App modules
from modules.cluster_names import *
from modules.py_postgres import *

# Tables
db_name = 'cluster_activities'
table_name = 'experiments'
conn = psycopg2.connect(database="{db}".format(db=db_name), \
                        user='rony', password='1234', host='localhost', port='5432')
results_cols_types = {'file_name': 'varchar', 'project_name': 'varchar', 'customer': 'varchar', \
                      'num_files': 'numeric', 'run_start': 'timestamp', 'run_end': 'timestamp',\
                      'processes': 'numeric', 'tasks_count': 'numeric', 'language_model': 'varchar',\
                      'clustering_method': 'varchar', 'clustering_params': 'varchar', 'n_clusters_perc': 'numeric',\
                      'num_clusters': 'numeric', 'tasks_per_cluster_mean': 'numeric',\
                      'tasks_per_cluster_median': 'numeric',\
                      'wcss': 'numeric', 'bcss': 'numeric', 'ch_index': 'numeric', 'duration_std': 'numeric'}


results_columns, data_types = list(results_cols_types.keys()), list(results_cols_types.values())

