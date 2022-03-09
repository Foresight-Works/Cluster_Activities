import sys
import os
import itertools
from itertools import combinations
from datetime import datetime
import sqlite3
import shutil
import subprocess
import re
import json
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
import Levenshtein
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
import gensim.downloader as api
from sklearn.cluster import SpectralClustering, AgglomerativeClustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import silhouette_score
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
extensions = config_vals('data', 'extensions')
ids_col, names_col, task_type = config.get('columns', 'id'),\
                                config.get('columns', 'name'), config.get('columns', 'type')
duration_cols = config_vals('columns', 'duration')
data_cols = [ids_col, names_col, task_type] + duration_cols
model_name = config.get('model', 'name')
n_clusters_percs = [float(n) for n in config_vals('model', 'n_clusters_perc')]
affinity = config.get('model', 'affinity')
data_format = config.get('data', 'format')
db_name = config.get('results', 'database')
table_name = config.get('results', 'table')
local_service = config.get('service', 'local')
num_executors = int(config.get('run', 'num_executors'))
min_cluster_size = int(config.get('model', 'min_cluster_size'))
print('min_cluster_size:', min_cluster_size)
response_type = config.get('model', 'response')

# Paths and Directories
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data', 'experiments')
results_dir = os.path.join(working_dir, 'results')
tokens_path = os.path.join(results_dir, 'tokens.txt')
matrices_dir = os.path.join(results_dir, 'matrices')
if 'matrices' not in os.listdir(results_dir):
    os.mkdir(matrices_dir)
models_dir = os.path.join(working_dir, 'models')

# App modules
from modules.build_references import *
from modules.utils import *
from modules.parsers import *
from modules.clustering import *
from modules.db_tables import *
from modules.evaluate import *
from modules.tokenizers import *
from modules.pipeline import *

# Tables
conn = sqlite3.connect('./results/CAdb', check_same_thread=False)
c = conn.cursor()
metrics_optimize = {'min_max_tpc': ('min', 1), 'wcss': ('min', 1), 'bcss': ('max', 1), 'ch_index': ('max', 1),\
'db_index':('min', 1), 'silhouette':('max', 1), 'words_pairs': ('max', 1)}
metrics_cols = {col:'TEXT' for col, v in metrics_optimize.items()}
#print('metrics_cols:', metrics_cols)
results_cols_types = {'experiment_id': 'TEXT', 'run_id': 'TEXT', 'file_name': 'TEXT',\
                      'num_files': 'TEXT', 'run_start': 'TEXT', 'run_end': 'TEXT', 'duration':'TEXT',\
                      'tasks_count': 'TEXT', 'language_model': 'TEXT', 'clustering_method': 'TEXT', 'clustering_params': 'TEXT',\
                      'num_clusters': 'TEXT', 'mean_duration_std':'TEXT',\
                      'tasks_per_cluster_mean': 'TEXT', 'tasks_per_cluster_median': 'TEXT',\
                      'min_tasks_per_cluster': 'TEXT', 'max_tasks_per_cluster': 'TEXT'}
results_cols_types = {**results_cols_types, **metrics_cols}
#print('results_cols_types:', results_cols_types)
#print('{n} result table columns'.format(n=len(results_cols_types)))
metrics_cols = list(metrics_cols.keys())
print('metrics columns:', metrics_cols)
results_columns, data_types = list(results_cols_types.keys()), list(results_cols_types.values())
create_table_statement = build_create_table_statement(table_name, results_columns, data_types)
c.execute(create_table_statement)


