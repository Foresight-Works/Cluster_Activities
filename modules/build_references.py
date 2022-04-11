from modules.libraries import *
from modules.config import *
from modules.tokenizers import *
from modules.utils import *

def reference_dictionaries(clustering_result, references_dir, distance_matrices):
    start = time.time()
    print('building reference dictionaries')
    np.save(os.path.join(references_dir, 'clustering_result.npy'), clustering_result)
    clusters, clusters_names = list(clustering_result.keys()), list(clustering_result.values())
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

    np.save(os.path.join(references_dir, 'names_tokens.npy'), names_tokens)
    print('{n} cluster_key tokens values in dictionary'.format(n=len(names_tokens)))
    print('examples:', list(names_tokens.items())[:2])

    # Reference list: Names pairs (names_pairs)
    # Reference dictionary: Names pairs per cluster(clusters_names_pairs)
    names_pairs, clusters_names_pairs = (), {}
    for cluster, clusters_names in clustering_result.items():
        clusters_name_pairs = tuple(combinations(clusters_names, 2))
        if clusters_name_pairs:
            names_pairs += clusters_name_pairs
            clusters_names_pairs[cluster] = clusters_name_pairs
    np.save(os.path.join(references_dir, 'clusters_names_pairs.npy'), clusters_names_pairs)
    print('{n} cluster_key pairs'.format(n=len(names_pairs)))
    print('example:', names_pairs[:2])
    print('{n} clusters_names_pairs'.format(n=len(clusters_names_pairs)))
    #print('example:', list(clusters_names_pairs.items())[:2])

    # Reference list: Tokens pairs (tokens_pairs)
    tokens_pairs = []
    for name_pair in names_pairs:
        name_pairs_tokens1, name_pairs_tokens2 = names_tokens[name_pair[0]], names_tokens[name_pair[1]]
        tokens_pairs += list(itertools.product(name_pairs_tokens1, name_pairs_tokens2))
    print('{n} token pairs'.format(n=len(tokens_pairs)))
    print('examples:', tokens_pairs[:2])

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
    print('{n} token pairs scores'.format(n=len(tokens_pairs_scores)))
    print('examples:', list(tokens_pairs_scores.items())[:2])
    np.save(os.path.join(references_dir, 'tokens_pairs_scores.npy'), tokens_pairs_scores)
    write_duration('scoring cluster_key pairs by matrices', start=start1)
    write_duration('References preparation', start=start)