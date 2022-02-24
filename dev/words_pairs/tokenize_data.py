import json
from setup import *
f = open('CCGT_878Clusters_validation_response.json', )
data = json.load(f)
# print(data)
score = 0
names = []
for cluster, cluster_names in data.items(): names += cluster_names
tokens = []
for name in names:
    tokens1 = tokenize(name, unique=True, exclude_stopwords=True, \
                       exclude_numbers=True, exclude_digit_tokens=True)
    tokens += tokens1

tokens = list(set(tokens))
print('{n1} names | {n2} tokens'.format(n1=len(names), n2=len(tokens)))

with open('./results/tokens.txt', 'w') as f:
    for t in tokens:
        f.write('{t}\n'.format(t=t))
