from setup import *
references_dir = sys.argv[1]
#references_dir = '/home/rony/Projects_Code/Cluster_Activities/results/CCGTD1_IPS/runs/0/references'
print('references_dir:', references_dir)
print(os.listdir(references_dir))
print('running words pairs')
# Read reference dictionaries
names_tokens, tokens_pairs_scores, clusters_names_pairs = {}, {}, {}
if 'names_tokens.npy' in os.listdir(references_dir):
    names_tokens = np.load(os.path.join(references_dir, 'names_tokens.npy'), allow_pickle=True)[()]
    print('names_tokens examples:', list(names_tokens.items())[:2])
if 'tokens_pairs_scores.npy' in os.listdir(references_dir):
    tokens_pairs_scores = np.load(os.path.join(references_dir, 'tokens_pairs_scores.npy'), allow_pickle=True)[()]
    print('tokens_pairs_scores examples:', list(tokens_pairs_scores.items())[:2])
if 'clusters_names_pairs.npy' in os.listdir(references_dir):
    clusters_names_pairs = np.load(os.path.join(references_dir, 'clusters_names_pairs.npy'), allow_pickle=True)[()]
    print('clusters_names_pairs examples:', list(clusters_names_pairs.items())[:2])

## Source: evaluate script ##
def scoreNamesPair(names_pair):
    name1, name2 = names_pair
    tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
    names_token_pairs = list(itertools.product(tokens1, tokens2))
    names_pair_score = 0
    for tokens_pair in names_token_pairs:
        names_pair_score += tokens_pairs_scores[tokens_pair]
        # print(tokens_pair, names_pair_score)
    return names_pair_score

def scoreCluster(cluster, cluster_name_pairs):
    cluster_score = 0
    tokens = []
    for names_pair in cluster_name_pairs:
        name1, name2 = names_pair
        tokens1, tokens2 = names_tokens[name1], names_tokens[name2]
        tokens = tokens + tokens1 + tokens2
        if len(tokens)==0:
            print('no tokens')
            print('names_pair:', names_pair)
            print(name1, name2)
        names_token_pairs = list(itertools.product(tokens1, tokens2))
        names_pair_score = 0
        for tokens_pair in names_token_pairs:
            names_pair_score += tokens_pairs_scores[tokens_pair]
        cluster_score += scoreNamesPair(names_pair)
    if len(tokens) == 0:
        print('no tokens after loop')
    cluster_score = cluster_score/len(tokens)
    return cluster, round(cluster_score, 2)


def scoreClusters(clusters, clusters_names_pairs, num_executors):
    executor = ProcessPoolExecutor(num_executors)
    clusters_scores = {}
    for cluster, cluster_score in executor.map(scoreCluster, clusters, clusters_names_pairs):
        print('cluster and score:', cluster, cluster_score)
        clusters_scores[cluster] = cluster_score
    executor.shutdown()
    #return round(sum(list(clusters_scores.values()))/len(clusters_scores), 2)
    return round(sum(list(clusters_scores.values())))

if __name__ == '__main__':
    clusters = list(clusters_names_pairs.keys())
    clusters_names_pairs = list(clusters_names_pairs.values())
    words_pairs_score = scoreClusters(clusters, clusters_names_pairs, num_executors)
    print('words_pairs_score:', words_pairs_score)
    with open(os.path.join(results_dir, 'words_pairs_score.txt'), 'w') as f: f.write(str(words_pairs_score))
    names_tokens, tokens_pairs_scores, clusters_names_pairs = {}, {}, {}