import boto3
import zipfile
import os
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
data_dir = '/home/rony/Projects_Code/Cluster_Activities/data/experiments'
file = 'CCGTD1_IPS_sample.zip'
file_path = os.path.join(data_dir, file)
#save_path='{d}/{f}'.format (d=directory,f=file)
#s3_client.upload_file(file_path, ds_bucket, save_path)
s3_client.upload_file(file_path, ds_bucket, file)
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']:
    print(key['Key'])
