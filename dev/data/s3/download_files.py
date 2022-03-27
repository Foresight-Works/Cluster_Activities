import boto3
import os
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
data_dir = '/home/rony/Projects_Code/Cluster_Activities/data/experiments'
file = 'CCGTD1_IPS_sample.zip'
if file in os.listdir('.'):
	os.remove(file)
file_path = os.path.join(data_dir, file)
s3.Bucket(ds_bucket).download_file(file, file)
if file in os.listdir('.'):
	print('file {f} downloaded'.format(f=file))
