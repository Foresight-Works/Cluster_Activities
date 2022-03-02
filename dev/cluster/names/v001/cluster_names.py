from tokens_similarity import *
from modules.tokenizers import *

def find_nearest(array, value):
    array = np.asarray(array)
    diff = np.abs(array - value)
    idx = (diff).argmin()
    return idx

def match_tokens(token1, tokens2, distances_matrix, cutoff=0.8):
     #print('token1:', token1)
     distances = [distances_matrix.at[token1, token2] for token2 in tokens2]
     distances_df = pd.DataFrame(list(zip(tokens2, distances)), columns=['token2', 'distance'])\
     .sort_values(by=['distance'], ascending=False)
     #print(distances_df)
     most_similar, most_similar_score = list(distances_df['token2'])[0], list(distances_df['distance'])[0]
     #print('most_similar:', most_similar)
     #print('most_similar_score:', most_similar_score)
     if most_similar_score < cutoff:
         most_similar = ''
     return most_similar

def find_matches(names, distances_matrix):
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

        matches = [m for m in matches if m]
        if matches:
            #print('matches:', matches)
            matches_lengths = [len(m.split(' ')) for m in matches]
            #print('matches_lengths:', matches_lengths)
            max_len, med_len = max(matches_lengths), np.median(matches_lengths)
            #print('matches_lengths max={ma} | median={me}'.format(ma=max_len, me=med_len))

            if max_len <= 5: match_len = max_len
            else: match_len = med_len
            #print('match_len:', match_len)
            nearest_match_index = find_nearest(matches_lengths, match_len)
            #print('nearest_match_index:', nearest_match_index)
            #for index, match in enumerate(matches): print(index, match)
            cluster_key = matches[nearest_match_index]
        else:
            #print('no matches found for:')
            #print(names)
            cluster_key = names[0]
        
        return cluster_key



def build_response(clustering_result, clusters_namesIDs, distances_matrix):
    response, validation_response = {}, {}
    for cluster_key, cluster_names in clustering_result:
        cluster_key = find_matches(cluster_names, distances_matrix)
        cluster_ids = clusters_namesIDs[cluster_key]
        response[cluster_key] = cluster_names
        validation_response[cluster_key] = cluster_ids
    response = json.dumps(response, indent=4)
    validation_response = json.dumps(validation_response, indent=4)
    return response, validation_response