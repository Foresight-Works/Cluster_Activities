import os
import sys

modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from libraries import *
from config import *
from modules.tokenizers import *


def test_uppercased_entities_text():
	print()
	print('test_uppercased_entities_text')
	test_data = open('./data/uppercase_chars.txt').read().split('\n')
	for text in test_data:
		tokens = text.split(' ')
		print(text, uppercased_entities_text(tokens))
	assert 2 + 2 == 4


# def test_build_uppercased_tokens_dict():
# 	test_data = open('./data/uppercase_chars.txt').read().split('\n')
# 	for text in test_data:
# 		tokens = text.split(' ')
# 		print()
# 		print(text)
# 		print(build_uppercased_tokens_dict(tokens))
# 	assert 2 + 2 == 4

def test_replace_uppercased():
	print()
	print('test_uppercased_entities_text')
	test_data = open('./data/uppercase_chars.txt').read().split('\n')
	for text in test_data:
		print('source:', text)
		source_tokens = text.split(' ')
		if uppercased_entities_text(source_tokens):
			print('Text has uppercased entities')
			uppercased_tokens_dict = build_uppercased_tokens_dict(source_tokens)
			print('uppercased_tokens_dict:', uppercased_tokens_dict)
			text = text.lower()
			print('lower cased:', text)
			text_tokens = text.split(' ')
			modified = replace_uppercased(text_tokens, uppercased_tokens_dict)
			print('modified:', modified)

	assert 2 + 2 == 4