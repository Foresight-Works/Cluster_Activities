import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
from config import *

def get_s3_paths(bucket_obj, dir):
	paths = []
	# Distance matrices paths
	for object_summary in bucket_obj.objects.filter(Prefix=dir):
		file_key = object_summary.key
		#print('file key:', file_key, file_key.split('/'))
		if file_key.split('/')[1]:
			paths.append(file_key)
	print('file paths:', paths)
	return paths

def download_s3_file(path, s3, bucket_name, local_dir):
	'''
	Download a file from an S3 bucket to the local directory
	:params path: s3 bucket Path to the file to downoload
	:params s3: s3 connection object
	:params bucket_name: The name of the bucket in which the file is stored
	:params local_dir: The name of the local directory in which to keep the downloaded matrices
	'''
	file = path.split('/')[1]
	file_path = os.path.join(local_dir, file)
	s3.Bucket(bucket_name).download_file(path, file_path)
	return file_path

def load_pickle_file(path, s3, bucket_name, local_dir):
	file_path = download_s3_file(path, s3, bucket_name, local_dir)
	return pd.read_pickle(file_path)

