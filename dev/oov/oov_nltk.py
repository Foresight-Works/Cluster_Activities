from nltk.corpus import words, wordnet
import time
start = time.time()
tokens = open('results/CCGT_D1_tokens.txt').read().split('\n')
results_path = 'results/CCGT_D1_oov_candidates.txt'
oov_candidates = []
for index, token in enumerate(tokens):
    print(index)
    if ((token not in words.words()) | (token not in wordnet.words())):
        oov_candidates.append(token)

end = time.time()
duration_secs = round(end - start, 2)
duration_mins = round(duration_secs/60, 2)
print('run duration: {ds} seconds, {dm} minutes'.format(ds=duration_secs, dm=duration_mins))

results_path = 'results/CCGT_D1_oov_candidates.txt'
with open(results_path, 'w') as f:
    for t in oov_candidates:
        f.write('{}\n'.format(t))


dict_tokens = [t for t in tokens if t not in oov_candidates]
results_path = 'results/CCGT_D1_dict_tokens.txt'
with open(results_path, 'w') as f:
    for t in dict_tokens:
        f.write('{}\n'.format(t))

for o in oov_candidates: print(o)