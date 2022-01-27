import os
files = os.listdir('../../data/raw_data')
for i, f in enumerate(files):
    j = i+1
    f = f.replace('.csv', '')
    print('{}.{}'.format(j, f))