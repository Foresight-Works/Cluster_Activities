# to add file metadata: https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
import os
import ast
import threading
from zipfile import ZipFile
import requests
import numpy as np
import pandas as pd
import pika
import json
# Service Location and parameters
from modules.config import *

def zip_files(file_names, data_path):
    '''
    Zip the files posted for analysis
    :param file_names (list): The names of the files posted for analysis
    :data_path (str): The absolute path to the directory storing the files to post   
    return (dict): A zipped copy of the files to analyse keyed by the 'file' key of the post command
    '''
    file_paths = {}
    for file in file_names:
        data_path = os.path.join(data_path, file)
        file_paths[file] = data_path
    with ZipFile('zipped_files.zip', 'w') as zip:
        for file, file_path in file_paths.items():
            zip.write(file_path, arcname=file)
    files_key_value = {'file': open('zipped_files.zip', 'rb')}
    os.remove('zipped_files.zip')
    return files_key_value

def results_consumer(experiment_id, conn):
    def print_message(channel, method, properties, body):
        message = json.loads(body)
        print('message:', message)
        run_cols = ['run_start', 'run_end', 'duration', 'tasks_count']
        result_df = pd.read_sql_query("SELECT * FROM results \
        WHERE experiment_id={eid}".format(eid=experiment_id), conn).drop(run_cols, axis=1)
        best_run_id = result_df['run_id'].values[0]
        print('Run id for the best run=', best_run_id)
        print('The clusters for the best run are ready for drill down analysis')

        # Show runs results
        print('Run for experiment {id}'.format(id=experiment_id))
        runs_df = pd.read_sql_query("SELECT * FROM runs \
        WHERE experiment_id={eid}".format(eid=experiment_id), conn).drop(run_cols, axis=1)
        print('** runs table **')
        print(runs_df)
        channel.queue_delete(queue=queue)
    queue = 'experiment_{id}'.format(id=experiment_id)
     # Consumer
    credentials = pika.PlainCredentials('rnd', 'Rnd@2143')
    parameters = pika.ConnectionParameters('172.31.34.107', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue, auto_delete=False)
    channel.exchange_declare(exchange=exchange, durable=True, exchange_type='direct')
    channel.basic_consume(queue, print_message, auto_ack=True)
    t1 = threading.Thread(target=channel.start_consuming)
    t1.start()
    t1.join(0)

## Configuration
min_cluster_size = 0
# Data
file_names = ['file_94810358.graphml']
print('file_names:', file_names)
files_key_value = zip_files(file_names, data_path)
experiment_ids = pd.read_sql_query("SELECT experiment_id from experiments", conn).astype(int)
if len(experiment_ids) == 0: experiment_id = 1
else: experiment_id = int(max(experiment_ids.values)[0]) + 1
print('experiment_id:', experiment_id)
response = requests.post(url, files=files_key_value, data={'experiment_id': experiment_id, 'service_location': service_location})
if response.text == 'Running clustering pipeline':
    results_consumer(experiment_id, conn)
