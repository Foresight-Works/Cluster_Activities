import sys
import os
import shutil
import numpy as np
import pandas as pd
import re
import time
from concurrent.futures import ProcessPoolExecutor
import nltk
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

from modules.utils import *
from modules.clustering import *

working_dir = os.getcwd()
modules_dir = os.path.join(working_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
data_dir = os.path.join(working_dir, 'data')
raw_data_dir = os.path.join(data_dir, 'raw_data')
results_dir = os.path.join(working_dir, 'results')

# Results directory and file
if 'results' in os.listdir():
    shutil.rmtree('results')
os.mkdir(results_dir)

