import sys
import os
import itertools
from itertools import combinations
from functools import reduce
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
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from scipy.spatial.distance import pdist
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
from collections import defaultdict
import string
import boto3