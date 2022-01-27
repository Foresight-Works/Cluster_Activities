import re

import pandas as pd
import nltk
from nltk.corpus import wordnet as wn
wnl = nltk.WordNetLemmatizer()
porter = nltk.PorterStemmer()
lancaster = nltk.LancasterStemmer()

pos_df = pd.read_pickle('./results/pos.pkl')
print('{} rows'.format(len(pos_df)))

# Stems and Lemmas
stems_lemmas = pos_df[['token', 'lemma']].drop_duplicates()\
    .rename(columns={'lemma': 'StanzaLemmatizer'})
tokens = list(stems_lemmas['token'])
stems_lemmas['WordNetLemmatizer'] = [wnl.lemmatize(t) for t in tokens]
stems_lemmas['PorterStemmer'] = [porter.stem(t) for t in tokens]
stems_lemmas['LancasterStemmer'] = [lancaster.stem(t) for t in tokens]
print(stems_lemmas.head())
stems_lemmas.to_excel('./results/stems_lemmas.xlsx', index=False)
#stems_lemmas = pd.read_excel('./results/stems_lemmas.xlsx')

# Progressive forms
indices = []
for index, row in stems_lemmas.iterrows():
    token, lemma = str(row['token']), str(row['StanzaLemmatizer'])
    if re.findall('ing$', token):
        if token == lemma:
            indices.append(index)
progressive_forms = stems_lemmas[stems_lemmas.index.isin(indices)]
progressive_forms.to_excel('progressive_forms.xlsx', index=False)

# Synonyms by Wordnet synsets
for token in tokens:
    syn_set = wn.synsets(token)
    for syn in syn_set:
        syn_lemmas = [l.name() for l in syn.lemmas()]
        print(syn.name(), syn_lemmas)
