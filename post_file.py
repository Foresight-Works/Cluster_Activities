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

def result_from_table(experiment_id, result_key='clusters'):
    result_df = pd.read_sql_query("SELECT * FROM results \
    WHERE experiment_id={eid}".format(eid=experiment_id), conn)
    result = result_df['result'].values[0]
    result = ast.literal_eval(result)
    return result[result_key]

# def results_consumer(experiment_id):
#     def get_results(channel, method, properties, body):
#         print('message:', body)
#         result = result_from_table(experiment_id)
#         print('result:', result)
#         channel.queue_delete(queue=queue)
#
#     # Consumer
#     queue = 'experiment_{id}'.format(id=experiment_id)
#     credentials = pika.PlainCredentials(rmq_user, rmq_password)
#     parameters = pika.ConnectionParameters(rmq_ip, rmq_port, '/', credentials)
#     connection = pika.BlockingConnection(parameters)
#     channel = connection.channel()
#     channel.queue_declare(queue=queue, auto_delete=False)
#     channel.exchange_declare(exchange=exchange, durable=True, exchange_type='direct')
#     channel.basic_consume(queue, get_results, auto_ack=True)
#     t1 = threading.Thread(target=channel.start_consuming)
#     t1.start()
#     t1.join(0)

## Configuration
min_cluster_size = 0
# Data
file_names = ['file_1391426496.graphml'] #['file_94810358.graphml']
print('file_names:', file_names)
files_key_value = zip_files(file_names, data_path)
experiment_ids = pd.read_sql_query("SELECT experiment_id from experiments", conn).astype(int)
if len(experiment_ids) == 0: experiment_id = 1
else: experiment_id = int(max(experiment_ids.values)[0]) + 1
print('experiment_id:', experiment_id)
print('url:', url)
response = requests.post(url, files=files_key_value, data={'experiment_id': experiment_id, 'service_location': serviceLocation})
if response.text == 'Running clustering pipeline':
    print(response.text)
    #results_consumer(experiment_id)
