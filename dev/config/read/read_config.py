from configparser import ConfigParser
config = ConfigParser()
config.read(r'./config.ini')
#print(config.get('model', 'language_model'))

