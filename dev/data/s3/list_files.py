import boto3
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

print("Bucket files")
files = []
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']: files.append(key)
print('files:', files)

print('Sub-Directory files')
ds_bucket_obj = s3.Bucket(ds_bucket)
dir = "matrices"
files = []
for object_summary in ds_bucket_obj.objects.filter(Prefix=dir):
    file_key = object_summary.key
    print(file_key, file_key.split('/'))
    if file_key.split('/')[1]:
        files.append(file_key)
print('files:', files)