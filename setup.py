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

# Data
data_file_name = 'project1.graphml'
project_name = data_file_name.split('.')[0]
ALLOWED_EXTENSIONS = ['graphml']
ids_col, names_col = ['ID', 'Label']

# Paths
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data')
raw_data_dir = os.path.join(data_dir, 'raw_data')
raw_data_path = os.path.join(raw_data_dir, data_file_name)
data_path = os.path.join(data_dir, data_file_name)
results_dir = os.path.join(working_dir, 'results')
tokens_file = 'tokens.txt'

# Model
model_name = 'AgglomerativeClustering'
model_params = {'affinity': 'euclidean'}
n_clusters_perc = 5

# Results directory and file
#if 'results' in os.listdir():
#    shutil.rmtree('results')
# os.mkdir(results_dir)

