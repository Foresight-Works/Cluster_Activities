from setup import *
from nltk.corpus import stopwords
punctuation_marks="=|\+|_|\.|:|\/|\*|\'|,|\?"
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

def normalize_entities(name, punctuation_symbols=punctuation_marks):
    '''
    Identify names in tokens by the presence of symbols
    '''
    #print('normalize f')
    #print('name:', name)
    name = name.replace('&amp','')
    tokens = name.split(' ')
    for token in tokens:
        if re.findall('\d', token):
            if re.findall('[A-Za-z]', token):
                name = name.replace(token, '<name>')
            else:
                name = name.replace(token, '<number')
        elif re.findall(punctuation_symbols, token):
            name = name.replace(token, '<name>')
    name = name.replace('<name> <name>', '<name>').replace('<number> <number>', '<number>')

    return name

def tokenize(data, unique=False, is_list=False, exclude_stopwords=False, exclude_chars=True,\
              split_backslah=True, split_hyphen=True, split_plus=True,\
              clean_punctuation=False, exclude_numbers=False, exclude_digit_tokens=False, \
              punctuation_symbols=punctuation_marks, stopwords=set(stopwords.words('english')),\
             normalized_entities=True):

    if is_list:
        data = [t for t in data if type(t)==str]
        data = ' '.join(data)
        data = re.sub('\s{2,}', ' ', data)

    # if exclude_parenthesis_terms:
    #     pattern= '\(.+?\)|\w*\d{1,}\.*\d{1,}\w*|\w+'
    #     data= re.sub(data, '', pattern)

    if normalized_entities:
        data = normalize_entities(data)
        pattern = '\<.+?\>|\w*\d{1,}\.*\d{1,}\w*|\w+'
        tokenizer = nltk.RegexpTokenizer(pattern)
        tokens = tokenizer.tokenize(data)
    else:
        tokens = nltk.word_tokenize(data)
    tokens = [t.lower() for t in tokens]
    if split_backslah: tokens = split_tokens (tokens, '/')
    if split_hyphen: tokens = split_tokens(tokens, '-')
    if split_plus: tokens = split_tokens(tokens, '+')

    if exclude_stopwords: tokens = [t for t in tokens if t not in stopwords]
    if clean_punctuation: tokens = [re.sub(punctuation_symbols, '', t) for t in tokens]
    if exclude_chars:tokens = [t for t in tokens if len(t) > 1]
    if exclude_numbers:
        tokens = [t for t in tokens if (not(isint(t)))]
        tokens = [t for t in tokens if (not(isfloat(t)))]
    if exclude_digit_tokens: tokens = [t for t in tokens if not re.findall('\d', t)]
    # Unique tokens preserving the tokens order in the input text
    if unique: tokens = sorted(set(tokens), key=tokens.index)
    return tokens