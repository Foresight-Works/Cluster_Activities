# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
import os
import ast
import threading
from zipfile import ZipFile
import mysql.connector as mysql
import requests
import numpy as np
import pandas as pd
import pika

# Service Location and parameters
service_location = 'Local' # Remote
url = 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering'
metrics_optimize = {'min_max_tpc': ('min', 1), 'wcss': ('min', 1), 'bcss': ('max', 1), 'ch_index': ('max', 1),\
'db_index':('min', 1), 'silhouette':('max', 1), 'words_pairs': ('max', 1)}
db_name = 'CAdb'
location_db_params = {'Local': {'host': 'localhost', 'user':'rony', 'password': 'exp8546$fs', 'database': db_name},\
                      'Remote': {'host': '172.31.36.11', 'user':'researchUIuser', 'password':'query1234$fs', 'database': db_name}}
conn_params = location_db_params[service_location]
conn = mysql.connect(**conn_params)
c=conn.cursor()
c.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
location_url = {'Local': 'http://127.0.0.01:6002/cluster_analysis/api/v0.1/clustering',\
                'Remote': 'http://172.31.36.11/cluster_analysis/api/v0.1/clustering'}
url = location_url[service_location]
print('url:', url)

def prepare_files(file_names, data_path):
    files = {}
    file_types = list(set([t.split('.')[1] for t in file_names]))
    print('file types:', file_types)
    # Checkpoint: Files submitted
    if file_names[0][0] == ' ':
        print('No file selected')
        file_checkpoints = False
    # Checkpoint: Zip file_names
    elif 'zip' in file_types:
        # Checkpoint: One among few files zipped
        if len(file_types) > 1:
            print('The submitted files include a zip file')
        else:
            data_path = os.path.join(data_path, file_names[0])
            files = {'file': open(data_path, 'rb')}
            # Zip data files
    else:
        file_paths = []
        for file in file_names:
            file_paths.append(os.path.join(data_path, file))
        print('file_paths:', file_paths)
        with ZipFile('zipped_files.zip', 'w') as zip:
            # writing each file one by one
            for file_path in file_paths:
                zip.write(file_path)
        files = {'file': open('zipped_files.zip', 'rb')}
        os.remove('zipped_files.zip')

    return files

# Consumer
EXCHANGE, QUEUE_NAME = 'kc.ca_research.exchange', 'kc.ca_research.queue'
class ThreadedConsumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
        parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, auto_delete=False)
        self.channel.exchange_declare(exchange=EXCHANGE, durable=True, exchange_type='direct')
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(QUEUE_NAME, on_message_callback=self.callback)
        threading.Thread(target=self.channel.basic_consume(QUEUE_NAME, on_message_callback=self.callback))

    def callback(self, channel, method, properties, body):
        message = ast.literal_eval(body.decode('utf-8'))
        print('message')
        print(message)
        np.save('message.npy', message)

    def run(self):
        self.channel.start_consuming()

def run_consumer():
    td = ThreadedConsumer()
    td.start()
    td.join(0)

## Configuration
min_cluster_size = 0
# Data
data_path = './data/experiments/'
file_names = ['CCGTD1_IPS_sample.zip']
print('file_names:', file_names)
files = prepare_files(file_names, data_path)
print(files)
if files:
    experiment_ids = pd.read_sql_query("SELECT experiment_id from results", conn).astype(int)
    if len(experiment_ids) == 0: experiment_id = 1
    else: experiment_id = int(max(experiment_ids.values)[0]) + 1
    print('experiment_id:', experiment_id)
    r = requests.post(url, files=files, data={'experiment_id': experiment_id})
    print('response:\n', r.text)
    run_consumer()
    message = np.load('message.npy', allow_pickle=True)[()]
    print('message:\n', message)
