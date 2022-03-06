from setup import *
def words_pairs (names, distances_matrices):
    matches, checked_token_pairs, checked_names_pairs, names_tokens = [], [], [], []
    similarity_score = 0
    for index1, name1 in enumerate(names):
        for index2, name2 in enumerate(names):
            tokens1 = tokenize(name1, unique=True, exclude_stopwords=True, \
                               exclude_numbers=True, exclude_digit_tokens=True)
            tokens2 = tokenize(name2, unique=True, exclude_stopwords=True, \
                               exclude_numbers=True, exclude_digit_tokens=True)
            tokens12 = tokens1 + tokens2
            names_tokens = names_tokens + tokens12

            unique_tokens12 = list(set(tokens12))
            tokens_matrices = []
            for matrix in distances_matrices:
                token_matrix = matrix[unique_tokens12][matrix.index.isin(unique_tokens12)]
                tokens_matrices.append(token_matrix)
                #print(token_matrix)

            for token1 in tokens1:
                token1_scores = []
                for token2 in tokens2:
                    pair_score = 0
                    for matrix in tokens_matrices:
                        # todo: lookup performance: hashing tokens in texts and in matrices so that
                        # row/cols headers are using the same indices, sort by the indices, df -> 2d array
                        # enhancing lookup as its not using sorted indices.
                        pair_score += matrix.at[token1, token2]
                    token1_scores.append(pair_score)
                token1_scores = [s for s in token1_scores if str(s) != 'nan']
                if token1_scores: token1_score = max(token1_scores)
                else: token1_score = 0
                similarity_score += token1_score

    unique_names_tokens = list(set(names_tokens))
    tokens_count = len(names_tokens)
    if tokens_count > 0:
        similarity_score = similarity_score/tokens_count
        similarity_score = round(similarity_score, 2)
    else: similarity_score = 0
    return similarity_score

# Paths
results_dir = '../results'
matrices_dir = os.path.join(results_dir, 'distance_matrices')
num_executors = 8

# Distance matrices
matrices_files = os.listdir(matrices_dir)
distance_matrices = []
for file in matrices_files:
    print('matrix file:', file)
    path = os.path.join(matrices_dir, file)
    df = pd.read_pickle(path)
    distance_matrices.append(df)
print('distance_matrices loaded')

# Data
f = open('../response/CCGT_878Clusters_validation_response.json', )
data = json.load(f)

# Score clusters
score = 0
for cluster, names in data.items():
    similarity = words_pairs(names, distance_matrices)
    print('===')
    for name in names: print(name)
    print('score=', similarity)

