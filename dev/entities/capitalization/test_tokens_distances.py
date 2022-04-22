import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = os.path.join(os.getcwd(), '../modules')
if modules_dir not in sys.path: sys.path.append(modules_dir)
from tokens_distances import *
from libraries import *
from config import *

# print(test_result.head())
# print(test_result.info())
#test_result.to_pickle('./data/embedding_scores_matrix.pkl')

def test_run_string_similarity_ratio():
	tokens = open('./data/tokens.txt').read().split()
	tokens = [t for t in tokens if t]
	expected_result = np.load('./data/tokens_scores.npy', allow_pickle=True)[()]
	test_result = run_string_similarity_ratio(tokens, num_executors)
	assert test_result == expected_result


def test_scores_to_matrix():
	fillna_value = 0
	expected_result = pd.read_pickle('./data/scores_matrix.pkl').sort_index().sort_index(axis=1)
	token_pairs_scores = np.load('./data/tokens_scores.npy', allow_pickle=True)[()]
	test_result = scoresToMatrix(token_pairs_scores, fillna_value)
	pd.testing.assert_frame_equal(test_result, expected_result)


def test_build_embeddings_distance_matrix():
	tokens = open('./data/tokens.txt').read().split()
	tokens = [t for t in tokens if t]
	expected_result = pd.read_pickle('./data/embedding_scores_matrix.pkl').sort_index().sort_index(axis=1)
	test_result = build_embeddings_distance_matrix(tokens, tokens_model)
	pd.testing.assert_frame_equal(test_result, expected_result)
	assert 2+2 == 4


