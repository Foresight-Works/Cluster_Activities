from configparser import ConfigParser
config = ConfigParser()
config.read(r'./config1.ini')
#print(config.get('model', 'language_model'))

