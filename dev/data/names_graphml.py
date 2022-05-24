from dev.pipeline.service.cluster_service5.setup import *
projects = parse_graphml_file(data_path)
names = list(projects[names_col])
print('{} cluster_key'.format(len(names)))

with open('cluster_key.txt', 'w') as f:
    for n in names:
        f.write('{n}\n'.format(n=n))
