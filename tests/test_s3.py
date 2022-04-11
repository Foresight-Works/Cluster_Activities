import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = os.path.join(os.getcwd(), '../modules')
if modules_dir not in sys.path: sys.path.append(modules_dir)

from libraries import *
from config import *

from aws.s3 import *

def test_get_s3_paths():
	paths = get_s3_paths(ds_bucket_obj, matrices_dir)
	print('paths:', paths)
	assert 1+1==2
