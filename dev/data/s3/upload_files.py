import boto3
import os
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
data_dir = '/home/rony/Projects_Code/Cluster_Activities/data/experiments'
files = os.listdir(data_dir)
for file in files:
    print('Uploading', file)
    file_path = os.path.join(data_dir, file)
    s3_client.upload_file(file_path, ds_bucket, file)
