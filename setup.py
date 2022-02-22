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
from configparser import ConfigParser

config = ConfigParser()
config.read(r'./config.ini')
project = config.get('paths', 'project_name')
working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data', project)
data_path = os.path.join(data_dir, config.get('paths', 'data_file'))
results_dir = os.path.join(working_dir, 'results', project)
if project in os.listdir('results'):
   shutil.rmtree(results_dir)
os.mkdir(results_dir)
with open(os.path.join(results_dir, 'tokens.txt'), 'w') as f: f.write(' ')

# App modules
from modules.utils import *
from modules.clustering import *
from modules.cluster_names import *
from modules.evaluate import *



