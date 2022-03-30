from setup import *
from build_references_functions import *
start = time.time()

# Response
f = open('response/CCGT_878Clusters_validation_response.json', )
response = json.load(f)
np.save(os.path.join(results_dir, 'response.npy'), response)
clusters, clusters_names = list(response.keys()), list(response.values())
unique_clusters = list(set(clusters))
print('{n1} clusters | {n2} unique clusters'.format(n1=len(clusters), n2=len(unique_clusters)))
names = []
for cluster_names in clusters_names: names += cluster_names
names = list(set(names))
print('{n} unique cluster_key'.format(n=len(names)))
names_tokens = {}

# Reference dictionary: Tokens per Name (names_tokens)
for name in names:
    tokens = tokenize(name, unique=True, exclude_stopwords=True, \
                       exclude_numbers=True, exclude_digit_tokens=True)
    names_tokens[name] = tokens
np.save(os.path.join(results_dir, 'names_tokens.npy'), names_tokens)
print('{n} cluster_key tokens values in dictionary'.format(n=len(names_tokens)))
print('examples:', list(names_tokens.items())[:2])

# Reference list: Names pairs (names_pairs)
# Reference dictionary: Names pairs per cluster(clusters_names_pairs)
names_pairs, clusters_names_pairs = (), {}
for cluster, clusters_names in response.items():
    clusters_name_pairs = tuple(combinations(clusters_names, 2))
    names_pairs += clusters_name_pairs
    clusters_names_pairs[cluster] = clusters_name_pairs
np.save(os.path.join(results_dir, 'clusters_names_pairs.npy'), clusters_names_pairs)
print('{n} cluster_key pairs'.format(n=len(names_pairs)))
print('example:', names_pairs[:2])
print('{n} clusters_names_pairs'.format(n=len(clusters_names_pairs)))
print('example:', list(clusters_names_pairs.items())[:2])

# Reference list: Tokens pairs (tokens_pairs)
tokens_pairs = []
for name_pair in names_pairs:
    name_pairs_tokens1, name_pairs_tokens2 = names_tokens[name_pair[0]], names_tokens[name_pair[1]]
    tokens_pairs += list(itertools.product(name_pairs_tokens1, name_pairs_tokens2))
np.save(os.path.join(results_dir, 'names_pairs.npy'), names_pairs)
print('{n} token pairs'.format(n=len(tokens_pairs)))
print('example:', tokens_pairs[0])

# Tokens
tokens = []
for name_tokens in names_tokens.values(): tokens += name_tokens
tokens = list(set(tokens))
print('{n} tokens'.format(n=len(tokens)))
with open(tokens_path, 'w') as f:
    for t in tokens:
        f.write('{t}\n'.format(t=t))

distance_matrices = []
# Embedding vectors
print('Embedding distance')
# tokens_embeddings = api.load("{m}".format(m=language_model_name))
# vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
# np.save(os.path.join(results_dir, 'vocab_embeddings.npy'), vocab_embeddings)
vocab_embeddings = np.load(os.path.join(results_dir, 'vocab_embeddings.npy'),  allow_pickle=True)[()]
# Embedding vectors distances: names_pairs_distances
embeddings_vectors = np.stack(list(vocab_embeddings.values()))
num_vectors = len(embeddings_vectors)
embedding_tokens = list(vocab_embeddings.keys())
names_pairs_indices = list(combinations(embedding_tokens, 2))
print('names_pairs_indices sample')
print(names_pairs_indices[:10])
embeddings_distances = pdist(embeddings_vectors)
embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
print('{n} embeddings_distances values'.format(n=len(embeddings_distances)))
print('embeddings_distances sample:', list(embeddings_distances.items())[:2])
distance_matrices.append(scoresToMatrix(embeddings_distances))

# LCS tokens distances: lcs_distances
print('LCS distance')
lcs_distances = lcs_scores(tokens_pairs, num_executors)
distance_matrices.append(scoresToMatrix(embeddings_distances))

for index, matrix in enumerate(distance_matrices):
    path = os.path.join(matrices_dir, 'matrix_{i}.pkl'.format(i=index))
    matrix.to_pickle(path)
    mat_df = pd.read_pickle(path)
    print(30 * '+')
    print(mat_df.head())

# Reference dictionaries: Tokens pairs - Similarity scores (tokens_pairs_scores)
start1 = time.time()
tokens_pairs_scores = {}
for token_pair in tokens_pairs:
    for matrix in distance_matrices:
        scores = []
        if all(t in matrix.columns for t in token_pair):
            score = matrix.at[token_pair[0], token_pair[1]]
        else: score = 0
        scores.append(score)
    tokens_pairs_scores[token_pair] = sum(scores)
np.save(os.path.join(results_dir, 'tokens_pairs_scores.npy'), tokens_pairs_scores)
print('{n} token pairs scores'.format(n=len(tokens_pairs_scores)))
print('examples:', list(tokens_pairs_scores.items())[:2])
write_duration('scoring cluster_key pairs by matrices', start=start1)
write_duration('References preparation', start=start)

from names_scoring import *
# Score
start1 = time.time()
print('scoring {n} clusters'.format(n=len(clusters)))
clusters_names_pairs = clusters_names_pairs.values()
eval_score = scoreClusters(clusters, clusters_names_pairs, num_executors)
print('eval_score:', eval_score)
write_duration('scoring', start1)
write_duration('process', start)