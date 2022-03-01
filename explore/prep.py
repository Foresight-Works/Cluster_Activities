# Main directories
import sys
import pandas as pd
import re
import os
import time
import nltk
from concurrent.futures import ProcessPoolExecutor
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

working_dir = '../' # os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'response/csvs')
results_dir = os.path.join(working_dir, 'results')
from utils import *
from clustering_methods import *

# Read response and extract activities
start_end_cols = ['Actual Start', 'Actual Completed', 'Current Planned Start', 'Current Planned Completed']
files = os.listdir(data_dir)
dfs = {}
names_projects_dicts = []
task_names = []
for file in files:
    df = pd.read_csv(os.path.join(data_dir, file))

    # Filter rows without start or end actual or planned dates
    df = df.dropna(how='any', subset=start_end_cols)
    df = df.dropna(axis=1, how='all')
    if 'Unnamed: 0' in df.columns: del df['Unnamed: 0']
    file = re.sub(' List --\d{2,}.csv', '', file)
    file = re.sub(' ', '_', file)

    # Tasks and Projects
    names_projects_dicts.append(dict(zip(df['Task Name'], df['Program'])))
    task_names += list(df['Task Name'])
    dfs[file] = df

