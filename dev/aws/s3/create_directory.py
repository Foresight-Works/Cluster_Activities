import boto3
import os
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

# Create Directory
dir = 'matrices'
s3_client.put_object(Bucket=ds_bucket, Key=(dir+'/'))

# Data
data_dir = '/matrices'
file = 'matrix_0.pkl'
file_path = os.path.join(data_dir, file)
s3_client.upload_file(file_path, ds_bucket, os.path.join(dir, file))

# List bucket files
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']:
    print(key['Key'])

# List directory files
ds_bucket = s3.Bucket(ds_bucket)
for object_summary in ds_bucket.objects.filter(Prefix="matrices/"):
    print(object_summary.key)