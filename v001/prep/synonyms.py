import re
import os
import pandas as pd
import nltk
import numpy as np
from nltk.corpus import wordnet as wn

def isint(value):
    '''
    Check if the input value type is integer
    '''
    try:
        int(value)
        return int(value)
    except ValueError:
        return False

results_dir = 'C:\\Users\\RonyArmon\\Projects_Code\\Cluster_Activities\\results'
pos_df = pd.read_pickle(os.path.join(results_dir,'pos.pkl'))
print('{} rows'.format(len(pos_df)))
print(pos_df.head())
lemmas = list(set(pos_df['lemma']))
print('{} lemmas'.format(len(lemmas)))
results = []
for lemma in lemmas:
    # Exclude numeric lemmas
    if type(isint(lemma))!=int:
        # Exclude single character lemmas
        if len(lemma)>1:
            # Exclude 2nd 3rd 4th
            if not re.findall('^\d{1,}[st|nd|rd|th]$', lemma):
                # Collect lemma synsets from Wordnet
                syn_set = wn.synsets(lemma)
                if syn_set:
                    synonyms = []
                    for syn in syn_set:
                        #syn_name = syn.name().split('.')[0]
                        #print(syn_name, syn_lemmas)
                        # Collect synonyms from all synsets
                        synonyms += [l.name() for l in syn.lemmas()]
                    synonyms = list(set(synonyms))
                    # Exclude multi word synonyms (e.g. 'survival_of_the_fittest'),
                    markers =  ['_', '-']
                    #synonyms = [s for s in synonyms if '_' not in s]
                    multi_words = [s for s in synonyms if any(m in s for m in markers)]
                    synonyms = [s for s in synonyms if s not in multi_words]
                    # Exclude proper nouns, such as names (e.g. Clarence_Day) and capitalized forms
                    synonyms = [s for s in synonyms if s == s.lower()]
                    # Exclude numeric synonyms
                    synonyms = [s for s in synonyms if type(isint(s))!=int]
                    # Exclude single character synonyms
                    synonyms = [s for s in synonyms if len(s)>1]
                    # Exclude lemma from synonyms
                    synonyms = [s for s in synonyms if s != lemma]
                    if synonyms:
                        for synonym in synonyms:
                            results.append([lemma, synonym])
lemmas_synonyms = pd.DataFrame(results, columns=['lemma', 'synonym'])
lemmas_synonyms.to_excel(os.path.join(results_dir, 'lemmas_synonyms.xlsx'), index=False)