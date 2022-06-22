import ast
def key_string_tuple(key):
	key = ast.literal_eval(key)
	key1 = tuple(key[0].replace("'", ''))
	key2 = key[1]
	key = (key1, key2)
	return key

key = '("(\'1\', \'Development And Mock Up\')", (\'not grouped\', \'not grouped\'))'
print(key_string_tuple(key))