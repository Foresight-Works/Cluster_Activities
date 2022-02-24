import spacy
#from spacy_wordnet.wordnet_annotator import WordnetAnnotator
# Load an spacy model (supported models are "es" and "en")
nlp = spacy.load('en_core_web_sm')
# Spacy 3.x
nlp.add_pipe("spacy_wordnet", after='tagger', config={'lang': nlp.lang})
# Spacy 2.x
# nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
token = nlp('prices')[0]

'''
ValueError: [E002] Can't find factory for 'spacy_wordnet' for language English (en). This usually happens when spaCy calls `nlp.create_pipe` with a custom component name that's not registered on the current language class. If you're using a Transformer, make sure to install 'spacy-transformers'. If you're using a custom component, make sure you've added the decorator `@Language.component` (for function components) or `@Language.factory` (for class components).
Issue raised: https://github.com/explosion/spaCy/discussions/10367
'''