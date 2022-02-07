from setup import *

raw_data = open(raw_data_path).read().split('</node>')
nodes = [s for s in raw_data if 'node id' in s]
nodes = [n.lstrip().rstrip() for n in nodes]
nodes = [n.replace('"', '') for n in nodes]
# Exclude file header
nodes = nodes[1:]

nodes_df = pd.DataFrame()
for node in nodes:
    node_rows = node.split('\n')
    id = re.findall('=(.*?)>', node_rows[0])[0]
    node_rows = node_rows[1:]
    print(30*'-')
    print('id:', id)
    print(node)
    print('node_rows:', node_rows)
    keys = [re.findall('=(.*?)>', n)[0] for n in node_rows]
    values = [re.findall('>(.*?)<', n)[0] for n in node_rows]
    node_dict = dict(zip(keys, values))
    node_df = pd.DataFrame([values], columns = keys)
    print('node dict:', node_dict)
    print(node_df)
    nodes_df = nodes_df.append(node_df)
print(nodes_df.head())
print(nodes_df.info())