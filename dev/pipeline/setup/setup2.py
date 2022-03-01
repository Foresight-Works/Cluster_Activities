import sys
import os
import shutil
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
#nltk.download('stopwords')

# Data
ALLOWED_EXTENSIONS = ['graphml']
ids_col, names_col = ['ID', 'Label']

# Paths
data_file = 'CCGT2files.zip'
project_name = 'CCGT'
data_dir = 'CCGT/graphmls/zipped'
tokens_file = 'tokens.txt'

working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, '../../modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'response', data_dir)
data_path = os.path.join(data_dir, data_file)
results_dir = os.path.join(working_dir, 'results')
# Results directory rewrite
if 'results' in os.listdir():
   shutil.rmtree('results')
os.mkdir(results_dir)
with open(os.path.join(results_dir, tokens_file), 'w') as f: f.write(' ')

# App odules

# Model
transformer_model = 'all-MiniLM-L6-v2'
model_name = 'AgglomerativeClustering'
model_params = {'affinity': 'euclidean'}
n_clusters_perc = 10
eval_metrics = ['cluster_duration_std', 'cluster_ss']