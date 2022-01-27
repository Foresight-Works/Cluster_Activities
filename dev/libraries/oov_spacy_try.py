import spacy
nlp = spacy.load('en_core_web_lg')
doc = nlp('I am sflmgmavknsaccasas dog cat bird bulbasaur')
print([tok.is_oov for tok in doc])
