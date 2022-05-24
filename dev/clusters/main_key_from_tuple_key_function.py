import numpy as np

def main_key_from_tuple_key(tuple_keyed_dictionary, key_position):
    '''
    Select the a key from a tuple key containing more than one elements
    :param tuple_keyed_dictionary(dict): A dictionary keyed by a tuple
    :param key_position: The tuple position holding the main key
    A value example:
    "('1', 'Customer Presentations')":
    [('CUS0080', 'Technical presentations and questions delivery to customer'),
    ('CUS0090', 'Customer Presentations')
    The key is "('1', 'Customer Presentations')" in which the main key is
    'Customer Presentations' in position 1
    '''
    main_key_dictionary = {}
    for k, v in tuple_keyed_dictionary.items():main_key_dictionary[ast.literal_eval(k)[key_position]] = v
    return main_key_dictionary

clusters = np.load('named_clusters.npy', allow_pickle=True)[()]['clusters']
cluster = list(clusters.items())[0]
# val = ("('1', 'Customer Presentations')", [('CUS0080', 'Technical presentations and questions delivery to customer'), ('CUS0090', 'Customer Presentations')])
key_ex = cluster[0]
import ast
b = ast.literal_eval(key_ex)
main_key_dictionary = main_key_from_tuple_key(clusters, 1)
print(main_key_dictionary)