import boto3
ds_bucket = 'foresight-ds-docs'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
s3.Object(ds_bucket, 'Test/').delete()
for key in s3_client.list_objects(Bucket=ds_bucket)['Contents']:
    print(key['Key'])
