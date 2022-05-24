import time
from modules.libraries import *
from modules.config import *

def build_result(data, clusters, names_col, ids_col):
    clustering_result = {}
    for cluster_key, cluster in enumerate(clusters):
        cluster_key_name = str(cluster_key+1)
        cluster_names = list(data[names_col][data['cluster'] == cluster])
        names_ids = list(data[ids_col][data['cluster'] == cluster])
        cluster_names_ids = list(zip(cluster_names, names_ids))
        clustering_result[cluster_key_name] = cluster_names_ids

    return clustering_result

def write_duration(process, start):
    '''
    Print process processes. Place the function following the last line for the process measured
    :param process(str): The name of the process measured
    :param start_time (time.time(): The start time for the process
    '''
    duration_secs = round(time.time() - start, 2)
    duration_mins = round(duration_secs / 60, 2)
    print('{p} took {ds} seconds, {dm} minutes'
          .format(p=process, ds=duration_secs, dm=duration_mins))

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

def tokens_count(tokens):
    counts = dict()
    for token in tokens:
        if token in counts:
            counts[token] += 1
        else:
            counts[token] = 1
    return counts

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

from scipy import stats
def x_outliers(x, threshold=3):

    '''
    Filter a list of values of outliers
    :params:
    x: A list of numeric values
    threshold: The outliers cutoff
    :return:
    The filtered list
    '''

    x = pd.DataFrame(x, columns=['value'])
    transformed = x[['value']].transform(stats.zscore)
    x['zscore'] = transformed
    x_vals = x['value'][x['zscore'] <= threshold]
    max_xvals = x_vals.max()
    return max_xvals

