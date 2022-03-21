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
import requests
from flask import Flask
from flask import Response, jsonify, request, redirect, url_for, send_from_directory
import socket
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer, util
from zipfile import ZipFile
import pika
import ast
import threading
import mysql.connector as mysql

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
headers = [ids_col, names_col, task_type] + duration_cols
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']
model_name = config.get('model', 'name')
n_clusters_percs = [float(n) for n in config_vals('model', 'n_clusters_perc')]
affinity = config.get('model', 'affinity')
data_format = config.get('data', 'format')
local_service = config.get('service', 'local')
if local_service == 'True':
    url = 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering'
else:
    url = 'http://172.31.36.11/cluster_analysis/api/v0.1/clustering'
num_executors = int(config.get('run', 'num_executors'))
min_cluster_size = int(config.get('model', 'min_cluster_size'))
response_type = config.get('model', 'response')

# Paths and Directories
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data', 'experiments')
results_dir = os.path.join(working_dir, 'results')
tokens_path = os.path.join(results_dir, 'tokens.txt')
matrices_dir = os.path.join(working_dir, 'matrices')
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
metrics_optimize = {'min_max_tpc': ('min', 1), 'wcss': ('min', 1), 'bcss': ('max', 1), 'ch_index': ('max', 1),\
'db_index':('min', 1), 'silhouette':('max', 1), 'words_pairs': ('max', 1)}
metrics_cols = {col: 'TEXT' for col, v in metrics_optimize.items()}
#print('metrics_cols:', metrics_cols)
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
db_name = 'CAdb'
conn_params = {'host': 'localhost', 'user': 'rony', 'password': 'exp8546$fs', 'database': db_name}