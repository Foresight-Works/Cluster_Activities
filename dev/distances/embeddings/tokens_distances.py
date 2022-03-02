from setup import *
start = time.time()
distance_matrices = []

tokens = open(tokens_path).read().split('\n')
print('{n} tokens'.format(n=len(tokens)))
tokens = [t for t in tokens if t]

start1 = time.time()
# Edit distances
tokens_pairs = tuple(combinations(tokens, 2))
print('{n} token pairs'.format(n=len(tokens_pairs)))
print('token pairs sample:', tokens_pairs[:2])

edit_distances = run_string_similarity_ratio(tokens_pairs, num_executors)
distance_matrices.append(scoresToMatrix(edit_distances))
write_duration('edit distances calculation', start1)

# Embedding vectors
start1 = time.time()
#print('Embedding distance')
language_model_name = config.get('language_models', 'tokens')
tokens_embeddings = api.load("{m}".format(m=language_model_name))
vocab_embeddings, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
with open(os.path.join(results_dir, 'not_in_embedding_vocabulary'), 'w') as f:
    for t in not_in_vocabulary: f.write('{t}\n'.format(t=t))
print('vocab_embeddings sample', list(vocab_embeddings.items())[:3])
#np.save(os.path.join(results_dir, 'vocab_embeddings.npy'), vocab_embeddings)
#vocab_embeddings = np.load(os.path.join(results_dir, 'vocab_embeddings.npy'),  allow_pickle=True)[()]
write_duration('loading embedding vectors', start1)

start1 = time.time()
# Embedding vectors distances: names_pairs_distances
embeddings_vectors = np.stack(list(vocab_embeddings.values()))
num_vectors = len(embeddings_vectors)
embedding_tokens = list(vocab_embeddings.keys())
names_pairs_indices = list(combinations(embedding_tokens, 2))
print('names_pairs_indices sample')
print(names_pairs_indices[:10])
embeddings_distances = pdist(embeddings_vectors, metric='euclidean')
embeddings_distances = dict(zip(names_pairs_indices, embeddings_distances))
print('{n} embeddings_distances values'.format(n=len(embeddings_distances)))
print('embeddings_distances sample:', list(embeddings_distances.items())[:2])
distance_matrices.append(scoresToMatrix(embeddings_distances))
write_duration('embedding matrix calculation', start1)

for index, matrix in enumerate(distance_matrices):
    path = os.path.join(matrices_dir, 'matrix_{i}.pkl'.format(i=index))
    matrix.to_pickle(path)
    mat_df = pd.read_pickle(path)
    print(30 * '+')
    print(mat_df.head())

write_duration('distances matrices calculation', start)