from modules.libraries import *
from modules.config import *
import re

def parse_graphml(file_name, graphml_str, headers):

    '''
    Parse a graphml file contents to a dataframe
    :param graphml_str (string): The file contents to parse
    :param headers (list): The columns to parse
    '''
    # Remove umlauts
    graphml_str = graphml_str.replace('�', '')
    nodes = graphml_str.split('</node>')
    nodes = [s for s in nodes if 'node id' in s]
    nodes = [n.lstrip().rstrip() for n in nodes]
    nodes = [n.replace('"', '') for n in nodes]
    # Exclude file header
    # nodes = nodes[1:]
    nodes_df = pd.DataFrame()
    print('parsing {n} nodes'.format(n=len(nodes)))
    for index, node in enumerate(nodes):
        node_rows = node.split('\n')
        node_rows = [r for r in node_rows if re.findall('<node id|<data key', r)]
        id = re.findall('=(.*?)>', node_rows[0])[0]
        node_rows = node_rows[1:]
        keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
        values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
        node_df = pd.DataFrame([values], columns = keys)
        nodes_df = pd.concat([nodes_df, node_df])
    nodes_df = nodes_df[headers]
    nodes_df['File'] = file_name
    return nodes_df

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
	file = os.path.basename(xer_file_path)
	graphml_file = file.replace('.xer', '.graphml')
	import jpype
	import mpxj
	if not jpype.isJVMStarted():
		jpype.startJVM()
	from net.sf.mpxj.reader import UniversalProjectReader
	from net.sf.mpxj import ActivityStatus
	from net.sf.mpxj import ActivityType

	project = UniversalProjectReader().read(xer_file_path)
	tasks = project.getTasks()
	task_features = {}
	for task in tasks:
		task_features, task_lines = {}, []
		task_features["id"] = task.getID()
		task_features["TaskType"] = str(task.getActivityType()).replace('TASK_DEPENDENT', 'TT_TASK')
		task_features["Label"] = task.getName()
		task_features["PlannedStart"] = task.getPlannedStart()
		task_features["PlannedEnd"] = task.getPlannedFinish()
		task_features["ActualStart"] = task.getActualStart()
		task_features["ActualEnd"] = task.getActualFinish()
		if task.getFreeSlack():
			task_features["Float"] = task.getFreeSlack().getDuration()
		else:
			task_features["Float"] = None

		task_features["Status"] = task.getActivityStatus()
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
		task_lines = '</node>'+'\n'+'\n'.join(task_lines)+'\n'
		with open(graphml_file, 'a') as f: f.write(task_lines)

	return graphml_file
	jpype.shutdownJVM()

