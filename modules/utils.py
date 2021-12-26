import time
from difflib import SequenceMatcher

def df_info(df):
    cols = df.columns
    rows_count = len(df)
    results = []
    for col in cols:
        null_count = df[col].isna().sum()
        coverage = round((rows_count - null_count) / rows_count, 2)
        uniques = len(df[col].unique())
        perc_uniques = round(100 * uniques / rows_count)
        results.append([col, coverage, uniques, perc_uniques])

    coverage_df = pd.DataFrame(results, columns=['column', 'coverage', 'uniques', '%uniques'])
    coverage_df['type'] = list(df.dtypes.values)
    coverage_df = coverage_df[coverage_df['coverage'] > 0].sort_values(by=['coverage'], ascending=False)

    return coverage_df

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


