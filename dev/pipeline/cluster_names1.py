import pandas as pd

from setup import *

distances_matrix = pd.read_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))
results = pd.read_excel('results.xlsx')
clusters = list(results['cluster'].unique())
cluster1 = clusters[0]
cluster1_names = list(results[names_col][results['cluster'] == cluster1])
from modules.tokens_similarity import *

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def match_tokens(token1, tokens2, distances_matrix):
     #print('token1:', token1)
     distances = [distances_matrix.at[token1, token2] for token2 in tokens2]
     distances_df = pd.DataFrame(list(zip(tokens2, distances)), columns=['token2', 'distance'])\
     .sort_values(by=['distance'], ascending=False)
     #print(distances_df)
     most_similar, most_similar_score = list(distances_df['token2'])[0], list(distances_df['distance'])[0]
     #print('most_similar:', most_similar)
     #print('most_similar_score:', most_similar_score)
     if most_similar_score < 0.8:
         most_similar = ''
     return most_similar

def find_matches(names):
    matches, checked_names, checked_tokens = [], [], []
    for index1, name1 in enumerate(names):
        if name1 not in checked: checked.append(name1)
        for index2, name2 in enumerate(names):
            match1 = ''
            if name1 != name2:
                #print(30 * '-' + '\n{n1}\n{n2}\n'.format(n1=name1, n2=name2))
                tokens1 = tokenize(name1, unique=False, exclude_stopwords=True, \
                      exclude_numbers=True, exclude_digit_tokens=True)
                tokens2 = tokenize(name2, unique=False, exclude_stopwords=True, \
                      exclude_numbers=True, exclude_digit_tokens=True)
                #print('tokens1:', tokens1)
                for token1 in tokens1:
                    if token1 not in checked_tokens:
                        checked_names.append(token1)
                        most_similar_token = match_tokens(token1, tokens2, distances_matrix)
                        #print('most_similar_token:', most_similar_token)
                        match1 += most_similar_token + ' '

            match1 = ' '.join(list(set(re.sub('\s{2,}', ' ', match1).rstrip().lstrip().split(' '))))
            #print('match1:', match1)

            #match1 = ' '.join(list(setsplit(' '))))
            matches.append(match1)

        matches_lengths = [len(m.split(' ')) for m in matches]
        max_len, med_len = max(matches_lengths), np.median(matches_lengths)
        #print('matches_lengths max={ma} | median={me}'.format(ma=max_len, me=med_len))

        if max_len <= 5: match_len = max_len
        else: match_len = med_len
        nearest_match_index = find_nearest(matches_lengths, med_len)
        #print('nearest_match_index:', nearest_match_index)
        cluster_key = matches[nearest_match_index]
        #print('match:', match)
        return cluster_key


for cluster in clusters:
    print('cluster', cluster)
    cluster_names = list(results[names_col][results['cluster'] == cluster])
    cluster_key = find_matches(cluster_names)
    print(30*'='+'\n{ck}\n--------'.format(ck=cluster_key))
    for n in cluster_names: print(n)
