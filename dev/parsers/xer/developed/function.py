import os
import pandas as pd
import re

def data_to_table(table_columns, table_data):
    return pd.DataFrame(data=table_data, columns=table_columns)
def read_xer(xer_file):
    line_types = ['%T', '%F', '%R', '%E']
    tables = dict()
    with open(xer_file, 'r', encoding='latin1') as xer:
        table_name, table_columns, table_data = None, [], []
        for line in xer:
            split_line = re.split("\t", line.replace('\n', ''))
            # skip lines not starting with a valid line type
            # (eg file info stuff)
            if split_line[0] not in line_types:
                continue
            # %T = table
            if split_line[0] == '%T':
                if table_name is not None:
                    try:
                        tables[table_name] = data_to_table(table_columns,
                                                           table_data)
                    except:
                        pass
                table_name = split_line[1]
                table_columns, table_data = [], []
            # %F = fields
            if split_line[0] == '%F':
                table_columns = split_line[1:]
            # %R = record
            # ERRORS WITH SOME TABLES?
            if split_line[0] == '%R':
                table_data.append(split_line[1:])
            # %E = end
            if split_line[0] == '%E' and table_name is not None:
                try:
                    tables[table_name] = data_to_table(table_columns,
                                                                   table_data)
                except:
                    pass
    return tables


dir = '/home/rony/Projects_Code/Cluster_Activities/data/MTR_Tunnels/xers'
files = os.listdir(dir)
file = files[0]
print('files:', files)
#for file in files:
path = os.path.join(dir, file)
tables = read_xer(path)

print(tables.keys())
for name, table in tables.items():
    print(60*'+')
    print(name)
    print(table.columns)