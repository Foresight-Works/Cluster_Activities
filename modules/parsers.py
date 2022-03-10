import re
from zipfile import ZipFile
import numpy as np
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', 100)
from setup import *

def parse_graphml(graphml_str):
    '''
    Parse a graphml file contents to a dataframe
    :param graphml_str (string): The file contents to parse
    :param headers (list): The columns to parse
    '''
    nodes = graphml_str.split('</node>')
    nodes = [s for s in nodes if 'node id' in s]
    nodes = [n.lstrip().rstrip() for n in nodes]
    nodes = [n.replace('"', '') for n in nodes]
    # Exclude file header
    nodes = nodes[1:]

    nodes_df = pd.DataFrame()
    for node in nodes:
        node_rows = node.split('\n')
        id = re.findall('=(.*?)>', node_rows[0])[0]
        node_rows = node_rows[1:]
        keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
        values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
        node_df = pd.DataFrame([values], columns = keys)
        nodes_df = nodes_df.append(node_df)

    return nodes_df[headers]

def parse_csv(csv_string):
    '''
    Parse a csv file contents to a dataframe
    :param csv_string (string): The file contents to parse
    :param headers (list): The columns to parse
    '''
    lines = csv_string.split('\n')
    source_headers = lines[0].split(',')
    indices = [source_headers.index(h) for h in headers]
    lines = [l for l in lines[1:] if l]
    rows = []
    for index, line in enumerate(lines):
        line_array = np.array(line.split(','))
        parsed_values = list(line_array[indices])
        rows.append(parsed_values)

    return pd.DataFrame(rows, columns=headers)


def xer_nodes(xer_file_path):
	print('xer_file_path:', xer_file_path)
	file = os.path.basename(xer_file_path)
	graphml_file = file.replace('.xer', '.graphml')
	import jpype
	import mpxj
	jpype.startJVM()
	from net.sf.mpxj.reader import UniversalProjectReader
	project = UniversalProjectReader().read(xer_file_path)
	tasks = project.getTasks()
	tasks_features = {}
	for task in tasks:
		task_features, task_lines = {}, []
		task_features["id"] = task.getID()
		task_features["TaskType"] = task.getActivityType()
		task_features["Label"] = task.getName()
		task_features["PlannedStart"] = task.getPlannedStart()
		task_features["PlannedEnd"] = task.getPlannedFinish()  # ?task.getPlannedFinish
		task_features["ActualStart"] = task.getActualStart()
		task_features["ActualEnd"] = task.getActualFinish()
		if task.getFreeSlack():
			task_features["Float"] = task.getFreeSlack().getDuration()
		else:
			task_features["Float"] = None
		task_features["Status"] = task.getActivityStatus()
		print('task features:', list(task_features.keys()))
		for feature, object in task_features.items():
			try:
				if object:
					object_str = object.toString()
				else:
					object_str = ''
			except AttributeError as e:
				object_str = str(object)
			if feature == 'id':
				line = '<node id="{o}">'.format(o=object_str)
			else:
				line = '<data key="{f}">{o}</data>'.format(f=feature, o=object_str)
			task_lines.append(line)
		print('task lines')
		task_lines = '</node>'+'\n'+'\n'.join(task_lines)+'\n'
		print(task_lines)
		with open(graphml_file, 'a') as f: f.write(task_lines)


	return graphml_file
	jpype.shutdownJVM()


def parse_files(raw_files):
    '''
    Parse graphml files and join the parsed products to a dataframe
    raw_files(dictionary): Files raw response keyed by the files' names
    '''
    parsed_dfs = pd.DataFrame()
    for name, file_data in raw_files.items():
        name = os.path.basename(name)
        format = name.split('.')[1]
        if format == 'graphml': parsed_df = parse_graphml(file_data)
        elif format == 'xer':
            print('xer format')
            xer_file_path = os.path.join(data_dir, name)
            parsed_df = xer_nodes(xer_file_path)
        elif format == 'csv': parsed_df = parse_csv(file_data)
        print('file: {n}, {r} tasks'.format(n=name, r=len(parsed_df)))
        parsed_dfs = parsed_dfs.append(parsed_df)
    return parsed_dfs