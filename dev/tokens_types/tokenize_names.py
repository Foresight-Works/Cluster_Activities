import pandas as pd
import time
import nltk
project_name = ''
results_file = project_name.replace(' ', '_')
results_path = './results/tokens.txt'.format(rf=results_file)
unique_names = open('../results/cluster_key.txt').read().split('\n')
print('{n} unique cluster_key tokenized'.format(n=len(unique_names)))
start = time.time()
names_tokens = []
for name in unique_names:
    tokens = nltk.word_tokenize(name)
    names_tokens += tokens

names_tokens = list(set(names_tokens))
names_tokens = [t.lower() for t in names_tokens if len(t)>1]
with open(results_path, 'w') as f:
    for t in names_tokens:
        f.write('{}\n'.format(t))

print('{n} token with more than one character identified in cluster_key'.format(n=len(names_tokens)))
end = time.time()
duration = round(end - start, 2)
print('run processes:', duration)



