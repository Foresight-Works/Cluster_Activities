import time
from difflib import SequenceMatcher

def similar(a, b):
    #return SequenceMatcher(None, a, b).ratio()
    #Treat blanks as "junk"
    return SequenceMatcher(lambda x: x == " ", a, b).ratio()


def cluster_names(name, names, checked, lower_sim, upper_sim):
    '''Calculate name similarity for input name compared to all names
    from a list of names and cluster names that are more similar than the
    specified threshold.
    '''
    cluster = [name]
    for name2 in names:
        if name2 not in checked:
            if (similar(name, name2) > lower_sim) \
                    & (similar(name, name2) < upper_sim):
                cluster.append(name2)
    return cluster


def cluster_names_df(name, names, lower_sim, upper_sim):
    '''Calculate name similarity for input name compared to all names
    from a list of names and cluster names that are more similar than the
    specified threshold.

    test:
    name = 'aaaa'
    namel = [name]
    names = ['eeaa', 'aaaa', 'aaab', 'aaac']
    cluster_names (name, names, 0.5 ,0.95)

    '''
    namel = [name]
    names_df = pd.DataFrame()
    names_df['query'] = [len(names) * namel][0]
    names_df['name'] = names
    names_df['distance'] = names_df.apply(lambda x: \
                                              similar(str(x['query']), str(x['name'])), axis=1)
    names_df = names_df[(names_df['distance'] > lower_sim) & (names_df['distance'] < upper_sim)]
    # print(names_df)
    cluster = list(names_df['name'])
    return cluster
