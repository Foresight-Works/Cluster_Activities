from setup import *
start = time.time()
distance_matrices = []

tokens = open(tokens_path).read().split('\n')
#print('{n} tokens'.format(n=len(tokens)))
tokens = [t for t in tokens if t]

start1 = time.time()
# Edit distances
tokens_pairs = tuple(combinations(tokens, 2))
#print('{n} token pairs'.format(n=len(tokens_pairs)))
#print('token pairs sample:', tokens_pairs[:2])

edit_distances = run_string_similarity_ratio(tokens_pairs, num_executors)
distance_matrices.append(scoresToMatrix(edit_distances, 1))
write_duration('edit distances calculation', start1)

# Embedding vectors
start1 = time.time()
#print('load embeddings')
language_model_name = config.get('language_models', 'tokens')
tokens_embeddings = api.load("{m}".format(m=language_model_name))
vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
with open(os.path.join(results_dir, 'not_in_embedding_vocabulary'), 'w') as f:
    for t in not_in_vocabulary: f.write('{t}\n'.format(t=t))
#print('vocab_embeddings sample', list(vocab_embeddings.items())[:3])
write_duration('loading embedding vectors', start1)

start1 = time.time()
# Embedding vectors distances: names_pairs_distances
embeddings_vectors = np.stack(list(vocab_embeddings.values()))
num_vectors = len(embeddings_vectors)
embedding_tokens = list(vocab_embeddings.keys())
names_pairs_indices = list(combinations(embedding_tokens, 2))
#print('names_pairs_indices sample')
#print(names_pairs_indices[:10])
embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
#print('{n} embeddings_distances values'.format(n=len(embeddings_distances)))
#print('embeddings_distances sample:', list(embeddings_distances.items())[:2])
embeddings_vectors = np.stack(list(vocab_embeddings.values()))
num_vectors = len(embeddings_vectors)
embedding_tokens = list(vocab_embeddings.keys())
names_pairs_indices = list(combinations(embedding_tokens, 2))
#print('names_pairs_indices sample')
#print(names_pairs_indices[:10])
embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
distance_matrix = scoresToMatrix(embeddings_distances, 0)
scaler = MinMaxScaler()
#print('distance_matrix')
#print(distance_matrix)
mn, mx = distance_matrix.min(), distance_matrix.max()
#print('mn, mx:', mn, mx)
mn, mx = min(mn), max(mx)
#print('mn, mx:', mn, mx)
scaled_matrix = (distance_matrix - mn) / (mx - mn)
scaled_matrix = scaled_matrix.replace(0, 1)
#print('scaled_matrix')
#print(scaled_matrix)
distance_matrices.append(scaled_matrix)
for index, matrix in enumerate(distance_matrices):
    path = os.path.join(matrices_dir, 'matrix_{i}.pkl'.format(i=index))
    matrix.to_pickle(path)
write_duration('distances matrices calculation', start)