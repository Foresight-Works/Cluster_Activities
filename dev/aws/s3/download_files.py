import boto3
import os
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
data_dir = '/data/experiments'
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']:
	file = key['Key']
	if file not in os.listdir(data_dir):
		file_path = os.path.join(data_dir, file)
		s3.Bucket(ds_bucket).download_file(file, file_path)
		print('file {f} downloaded'.format(f=file))

