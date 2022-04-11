import re

import boto3
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
ds_bucket_obj = s3.Bucket(ds_bucket)

# Directory with files to delete
dir = "matrices"

# List files to delete
files = []
for object_summary in ds_bucket_obj.objects.filter(Prefix=dir):
    file_key = object_summary.key
    if file_key.split('/')[1]:
        files.append(file_key)

print('files to delete:', files)

# Delete
for file in files: s3.Object(ds_bucket, file).delete()

files = []
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']: files.append(key['Key'])
print('Bucket files following deletion:', files)
