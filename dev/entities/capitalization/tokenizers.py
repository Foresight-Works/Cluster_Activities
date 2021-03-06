from modules.libraries import *
from modules.config import *
from nltk.corpus import stopwords
print('tokenizers imported')

punctuation_marks="=|-|\+|_|\.|:|\/|\*|\'|,|\?"
def isfloat(value):
    '''
    Check if the input value type is float
    '''
    try:
        float(value)
        return True
    except ValueError:
        return False

def isint(value):
    '''
    Check if the input value type is integer
    '''
    try:
        int(value)
        return True
    except ValueError:
        return False

def split_tokens (tokens, splitter):
    tokens_splitter= [t for t in tokens if splitter in t]
    tokens = [t for t in tokens if splitter not in t]
    for t in tokens_splitter: tokens += t.split(splitter)
    return tokens

def uppercase_characters(token):

    '''
    Check if all characters in the input token are uppercased
    '''

    uppercased = False
    c = 0
    for l in token:
        if l.isupper():
            c += 1
    if c == len(token): uppercased = True
    return uppercased


def uppercased_entities_text(tokens):

    '''
    Check if all token characters in a list of input tokens are uppercased
    '''
    uppercased_in = False
    for token in tokens:
        if uppercase_characters(token):
            uppercased_in = True
            break
    return uppercased_in

def build_uppercased_tokens_dict(tokens):
    '''
    Build a dictionary of tokens connecting their lowercased (key) to uppercased (value) formats
    '''
    uppercased_tokens_dict = {}
    for token in tokens:
        if uppercase_characters(token):
            uppercased_tokens_dict[token.lower()] = token
    return uppercased_tokens_dict


def replace_uppercased(text_tokens, uppercased_tokens_dict):
    '''
    Replace text tokens by their uppercased forms given in uppercased_tokens_dict
    :params source_tokens(list): The tokens of the source text which include the uppercased tokens in their uppercase formats
    :params text_tokens(list): The tokens of the text to modify
    :params uppercased_tokens_dict (dict): a dictionary of tokens connecting their lowercased (key) to uppercased (value) formats
    return:
    A list of the texts' modified tokens
    '''

    text_tokens1 = []
    for token in text_tokens:
        if token in list(uppercased_tokens_dict.keys()):
            print(token, uppercased_tokens_dict[token])
            token1 = uppercased_tokens_dict[token]
        else:
            token1 = token
        text_tokens1.append(token1)
    text_tokens = text_tokens1
    return text_tokens


def normalize(text, punctuation_marks=punctuation_marks):
    '''
    Identify texts in tokens by the presence of symbols
    '''
    #print('normalize f')
    #print('text:', text)
    text = text.replace('&amp', '')
    tokens = text.split(' ')
    for token in tokens:
        # Entities and Numbers
        if re.findall('\d', token):
            if re.findall('[A-Za-z]', token):
                text = text.replace(token, '<name>')
            else:
                text = text.replace(token, '<number>')
        elif re.findall(punctuation_marks, token):
            text = text.replace(token, '<name>')

    text = text.replace('<name> <name>', '<name>').replace('<number> <number>', '<number>')
    return text

def tokenize(text, unique=False, exclude_stopwords=False, exclude_chars=True,\
              split_backslah=True, split_hyphen=True, split_plus=True, exclude_parenthesis_terms=False,\
              clean_punctuation=False, exclude_numbers=False, exclude_digit_tokens=False, \
              punctuation_marks=punctuation_marks, stopwords=set(stopwords.words('english')),\
              normalized_entities=True):
    if exclude_parenthesis_terms:
        pattern= '\(.+?\)|\w*\d{1,}\.*\d{1,}\w*|\w+'
        text= re.sub(text, '', pattern)

    if normalized_entities:
        text = normalize(text)
        pattern = '\<.+?\>|\w*\d{1,}\.*\d{1,}\w*|\w+'
        tokenizer = nltk.RegexpTokenizer(pattern)
        tokens = tokenizer.tokenize(text)
    else:
        tokens = nltk.word_tokenize(text)
    tokens = [t.lower() for t in tokens]
    if split_backslah: tokens = split_tokens (tokens, '/')
    if split_hyphen: tokens = split_tokens(tokens, '-')
    if split_plus: tokens = split_tokens(tokens, '+')

    if exclude_stopwords: tokens = [t for t in tokens if t not in stopwords]
    if clean_punctuation: tokens = [re.sub(punctuation_marks, '', t) for t in tokens]
    if exclude_chars:tokens = [t for t in tokens if len(t) > 1]
    if exclude_numbers:
        tokens = [t for t in tokens if (not(isint(t)))]
        tokens = [t for t in tokens if (not(isfloat(t)))]
    if exclude_digit_tokens: tokens = [t for t in tokens if not re.findall('\d', t)]
    # Unique tokens preserving the tokens order in the input text
    if unique: tokens = sorted(set(tokens), key=tokens.index)
    return tokens

def normalize_texts(texts, test='names1.txt'):
    normalized_texts = []
    for text in texts:
        normalized_texts.append(normalize(text))
    return normalized_texts

def tokenize_texts(texts, unique=False, test='names1.txt', **kwargs):
    tokenized_texts = []
    for text in texts:
        tokenized_texts += tokenize(text, **kwargs)
    if unique: tokenized_texts = sorted(set(tokenized_texts), key=tokenized_texts.index)
    return tokenized_texts


def tokens_count(tokens):
    counts = dict()
    for token in tokens:
        if token in counts:
            counts[token] += 1
        else:
            counts[token] = 1
    return counts

def get_tokens_locations(parts):
    tokens_locations = defaultdict(list)
    for part in parts:
        tokens = tokenize(part, unique=True, exclude_stopwords=False, \
                          exclude_numbers=True, exclude_digit_tokens=True)
        tokens_indices = [tokens.index(t) for t in tokens]
        for token in tokens:
            tokens_locations[token].append(tokens_indices[tokens.index(token)])
    tokens_typical_locations = {}
    for token, locations in tokens_locations.items():
        token_typical_location = max(set(locations), key=locations.count)
        tokens_typical_locations[token] = token_typical_location

    return tokens_typical_locations