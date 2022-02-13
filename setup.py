import sys
import os
import shutil
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

# Data
ALLOWED_EXTENSIONS = ['graphml']
ids_col, names_col = ['ID', 'Label']

# Paths
raw_data_file = 'zipped_files2.zip'
project_name = 'CCGT'
data_dir = 'CCGT_graphmls_zipped'
raw_data_dir = 'CCGT/graphmls/zipped'
tokens_file = 'tokens.txt'

working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data', data_dir)
raw_data_dir = os.path.join(working_dir, 'data/raw_data/', raw_data_dir)
raw_data_file = os.path.join(raw_data_dir, raw_data_file)
results_dir = os.path.join(working_dir, 'results')
# Results directory rewrite
if 'results' in os.listdir():
   shutil.rmtree('results')
os.mkdir(results_dir)
with open(os.path.join(results_dir, tokens_file), 'w') as f: f.write(' ')

# App odules
from modules.utils import *
from modules.clustering import *
from modules.cluster_names import *

# Model
model_name = 'AgglomerativeClustering'
model_params = {'affinity': 'euclidean'}
n_clusters_perc = 10


