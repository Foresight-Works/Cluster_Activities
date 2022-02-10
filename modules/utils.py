import pandas as pd
import time
from difflib import SequenceMatcher
from setup import *
def allowed_file(filename):
    """ Tests if filetype is an allowed filetype """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse_graphml_file(file_path):
    raw_data = open(file_path).read().split('</node>')
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
        keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
        values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
        node_df = pd.DataFrame([values], columns=keys)
        nodes_df = nodes_df.append(node_df)
    return nodes_df


def parse_graphml_files(file_paths):
    '''
    Parse graphml files
    file_paths (list): Paths to the files to parse
    '''
    nodes_df = pd.DataFrame()
    print('===parsing graphml files===')
    for file_path in file_paths:
        print('file_path:', file_path)
        file_name = re.findall('(\w+)\.graphml', file_path.replace(' ', '_'))[0]
        raw_data = open(file_path).read().split('</node>')
        #print('raw data:', raw_data)
        nodes = [s for s in raw_data if 'node id' in s]
        nodes = [n.lstrip().rstrip() for n in nodes]
        nodes = [n.replace('"', '') for n in nodes]
        # Exclude file header
        nodes = nodes[1:]
        print('{} nodes'.format(len(nodes)))
        for node in nodes:
            node_rows = node.split('\n')
            id = re.findall('=(.*?)>', node_rows[0])[0]
            node_rows = node_rows[1:]
            keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
            values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
            node_df = pd.DataFrame([values], columns=keys)
            node_df['source_file'] = file_name
            nodes_df = nodes_df.append(node_df)

    print('{} all nodes'.format(len(nodes_df)))
    return nodes_df



def df_info(df):
    cols = df.columns
    rows_count = len(df)
    results = []
    for col in cols:
        null_count = df[col].isna().sum()
        coverage = round((rows_count - null_count) / rows_count, 2)
        uniques = len(df[col].unique())
        perc_uniques = round(100 * uniques / rows_count, 2)
        results.append([col, coverage, uniques, perc_uniques])

    coverage_df = pd.DataFrame(results, columns=['column', 'coverage', 'uniques', '%uniques'])
    coverage_df['type'] = list(df.dtypes.values)
    coverage_df = coverage_df[coverage_df['coverage'] > 0].sort_values(by=['coverage'], ascending=False)
    return coverage_df


def lists_to_dict_df(list_a, list_b, col_a=None, col_b=None, result_as='dict'):

    '''
    Build a dictionary or a dataframe from two input lists
    :params:
    list_a, list_b: The lists to zip into a dictionary or use as dataframe columns
    col_a, col_b: The dataframe column headers
    result_as: The output format
    :returns:
    A dictionary if results_as = 'dict', else a dataframe
    '''

    list_b = [float(s) for s in list_b]
    if result_as == 'dict':
        combined = dict(zip(list_a, list_b))
    else:
        combined = pd.DataFrame(list(zip(list_a, list_b)), \
             columns=[col_a, col_b])
        combined = combined.sort_values(by=col_b, ascending=False)
    return combined


def count_names(companies_df):
    task_names = companies_df['activity_name'][companies_df['activity_type']=='TT_Task']
    unique_tasks = task_names.unique()
    names_counts = task_names.value_counts()
    single_repeat = len(names_counts[names_counts==1])
    names_counts = names_counts[names_counts>1]
    names_counts = pd.DataFrame(list(zip(list(names_counts.index), list(names_counts.values))), columns = ['name','count'])\
    .sort_values(by='count', ascending=False)
    print('The dataset holds {n} tasks, {n1} of them are unique'.format(n=len(task_names), n1=len(unique_tasks)))
    print('{n} tasks repeat only once and {n1} tasks repeat more than once'.format(n=single_repeat, n1=len(names_counts)))

    return(names_counts)


def filter_empty_columns(df):
    empty_cols, rows_count = [], len(df)
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count == rows_count: empty_cols.append(col)
    keep = [c for c in df.columns if c not in empty_cols]
    return df[keep]

def write_name_cluster(results_path, name, cluster):
    before, after = 90*'+'+'\n', 90*'-'+'\n'
    name_string = 'key name:{n}\n'.format(n=name)
    cluster_string = ''
    for c in cluster:
        c = c + '\n'
        cluster_string += c
    result = before + name_string + after + cluster_string
    with open(results_path, 'a') as f:
        f.write(result)


