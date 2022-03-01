import os
s = 'abc'
print(os.environ)
print(list(os.environ.keys()))
os.environ['PYTHONHASHSEED'] = '10'
print('Hashseed is', os.environ['PYTHONHASHSEED'])
print('hash of s is', hash(s))