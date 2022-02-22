from setup import *


def parse_graphml_file(graphml_str, headers):
    '''
    Parse a graphml file contents to a dataframe
    :param graphml_str (string): The file contents to parse
    :param headers (list): The columns to parse
    '''
    nodes = [s for s in graphml_str if 'node id' in s]
    nodes = [n.lstrip().rstrip() for n in nodes]
    nodes = [n.replace('"', '') for n in nodes]
    # Exclude file header
    nodes = nodes[1:]

    nodes_df = pd.DataFrame()
    for node in nodes:
        node_rows = node.split('\n')
        id = re.findall('=(.*?)>', node_rows[0])[0]
        node_rows = node_rows[1:]
        keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
        values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
        node_df = pd.DataFrame([values], columns = keys)
        nodes_df = nodes_df.append(node_df)

    return nodes_df[headers]


def parse_csv(csv_string, headers):
    '''
    Parse a csv file contents to a dataframe
    :param csv_string (string): The file contents to parse
    :param headers (list): The columns to parse
    '''
    print('headers to parse:', headers)
    lines = csv_string.split('\n')
    source_headers = lines[0].split(',')
    print('source_headers:', source_headers)
    indices = [source_headers.index(h) for h in headers]
    print('headers indices:', indices)
    lines = [l for l in lines[1:] if l]
    rows = []
    for index, line in enumerate(lines):
        line_array = np.array(line.split(','))
        parsed_values = list(line_array[indices])
        rows.append(parsed_values)

    return pd.DataFrame(rows, columns=headers)

