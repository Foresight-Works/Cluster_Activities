from setup import *

# todo: update upload or pipeline to allow more then one project in the data path
projects = parse_graphml_file(data_path)
names = list(projects[names_col])
print('{} names'.format(len(names)))

with open('names.txt', 'w') as f:
    for n in names:
        f.write('{n}\n'.format(n=n))
