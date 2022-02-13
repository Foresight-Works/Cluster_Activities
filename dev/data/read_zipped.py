from zipfile import ZipFile
path = '/home/rony/Projects_Code/Cluster_Activities/data/raw_data/CCGT_graphmls_zipped/files.zip'
unzipped_files = ZipFile(path)
file_names = unzipped_files.namelist()
print('file_names:', file_names)
for file_name in file_names:
    print('===={f}===='.format(f=file_name))
    a_file = unzipped_files.read(file_name)
    a_file = a_file.decode()
    print(type(a_file))
    print(a_file)