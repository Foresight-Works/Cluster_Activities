import boto3
import os
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
data_dir = '/data/experiments'
file = 'CCGTD1_IPS_sample.zip'
file_path = os.path.join(data_dir, file)
s3_client.upload_file(file_path, ds_bucket, file)
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']:
    print(key['Key'])
