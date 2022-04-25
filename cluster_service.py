import os
import sys
modules_dir = os.path.join(os.getcwd(), 'modules')
if modules_dir not in sys.path:
    sys.path.append(modules_dir)
from libraries import *
from config import *
from parsers import *
from pipeline import *

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir

# Prepare data and run pipeline
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def run_service():
    # Experiment set up
    experiment_id = request.values.get('experiment_id', ' ')
    print('experiment_id posted:', experiment_id)
    experiment_dir_name = 'experiment_{id}'.format(id=experiment_id)
    client = request.values.get('client', ' ')
    print('client:', client)
    min_cluster_size = request.values.get('min_cluster_size', ' ')
    if min_cluster_size == ' ': min_cluster_size = 0
    else: min_cluster_size = int(min_cluster_size)
    print('min_cluster_size:', min_cluster_size)
    service_location = request.values.get('service_location', ' ')
    conn_params = location_db_params[service_location]
    print('conn_params:', conn_params)
    conn = mysql.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("INSERT INTO experiments (experiment_id) VALUES ({id})".format(id=experiment_id))
    conn.commit()
    n_clusters_posted = int(request.values.get('num_clusters', '-1'))
    print('n_clusters_posted:', n_clusters_posted)

    experiment_dir = os.path.join(results_dir, experiment_dir_name)
    if experiment_dir_name not in os.listdir(results_dir):
        os.mkdir(experiment_dir)
    runs_dir = os.path.join(experiment_dir, 'runs')
    if 'runs' not in os.listdir(experiment_dir):
        os.mkdir(runs_dir)
    for metric, optimize in metrics_optimize.items():
        posted_value = request.values.get(metric, ' ')
        if posted_value == ' ': posted_value = 1
        else: posted_value = int(posted_value)
        metrics_optimize[metric] = (metrics_optimize[metric][0], int(posted_value))
    print('metrics optimized:', metrics_optimize)

    # Data
    zipped_files = request.files.get('file', '')
    zipped_files.save('temp.zip')
    zipped_object = ZipFile('temp.zip', "r")
    if 'temp.zip' in os.listdir(): os.remove('temp.zip')
    file_names = zipped_object.namelist()
    print('file_names:', file_names)
    projects = pd.DataFrame()
    if file_names:
        num_files = len(file_names)
        # File cluster_key to pass to the results table (temp. proxy for experiment name)
        file_names_str = [f.split('.')[0].replace('tmp/', '') for f in file_names]
        file_names_str = r'*'.join(file_names_str).rstrip(r'*')
        # File name validation
        for file_name in file_names:
            file_type = file_name.split('.')[1]
            if file_type in extensions:
                print('===={f}===='.format(f=file_name))
                encodings = ['utf-8-sig', 'latin-1', 'ISO-8859-1', 'Windows-1252']
                encoded, index = False, 0
                while encoded == False:
                    encoding = encodings[index]
                    print('encoding using', encoding)
                    try:
                        file_posted = zipped_object.read(file_name).decode(encoding=encoding)
                        encoded = True
                    except UnicodeDecodeError as e:
                        print(e)
                        index += 1
                format = file_name.split('.')[1]
                if format == 'graphml':
                    parsed_df = parse_graphml(file_name, graphml_str, headers)
                elif format == 'xer':
                    print('xer format')
                    xer_lines = file_posted.split('\n')
                    print('xer_lines sample:', xer_lines[:10])
                    with open('tmp_data_file.xer', 'w') as f:
                        for line in xer_lines: f.write('{l}\n'.format(l=line))
                    graphml_file = xer_nodes('tmp_data_file.xer')
                    os.remove('tmp_data_file.xer')
                    graphml_str = open(graphml_file).read()
                    os.remove(graphml_file)
                    parsed_df = parse_graphml(file_name, graphml_str, headers)

                elif format == 'csv':
                    parsed_df = parse_csv(file_posted)
                print('file: {n}, {r} tasks'.format(n=file_name, r=len(parsed_df)))
                projects = pd.concat([projects, parsed_df])

        # Remove tmp files
        file_types = ['xer', 'graphml']
        for file_type in file_types:
            tmp_file = 'tmp_data_file.{ft}'.format(ft=file_type)
            if tmp_file in os.listdir(): os.remove(tmp_file)

        # Projects TDAs
        print(projects.columns)
        projects['Label'] = [name.replace('&amp', '') for name in list(projects['Label'])]
        print('Projects')
        print(projects.head())
        print(projects.info())
        print('task type values:', projects[task_type].unique())
        print(projects[task_type].value_counts())
        projects = projects[projects[task_type].isin(['TT_TASK', 'TT_Task'])]
        # Drop duplicates
        rows_count1 = len(projects)
        print('rows count, all rows=', rows_count1)
        projects = projects.drop_duplicates()
        rows_count2 = len(projects)
        duplicates_count = int(rows_count1 - rows_count2)
        print('rows count, no duplicates=', rows_count2)
        print('{n} duplicate tasks dropped'.format(n=rows_count1-rows_count2))

        # A {task id: source file} dictionary to make the file name per task available for the RCF analysis in the research UI
        ids_files = dict(zip(list(projects['ID']), list(projects['File'])))
        projects.to_excel(os.path.join(experiment_dir, 'parsed_data.xlsx'), index=False)
        tasks_count = len(projects)
        print('{n} tdas'.format(n=tasks_count))
        print('projects')
        print(projects.head())
        print(projects.info())

        if len(projects) > 0:
            print('file_names_str to pipeline:', file_names_str)
            run_pipeline_args = (projects, experiment_id, client, experiment_dir, runs_dir, num_files, file_names_str, \
                         runs_cols, results_cols, metrics_cols, metrics_optimize, conn_params,\
                         min_cluster_size, n_clusters_posted, duplicates_count, ids_files)
            pipeline = threading.Thread(target=run_pipeline, args=run_pipeline_args)
            pipeline.start()
            pipeline.join(0)
            return 'Running clustering pipeline'

        else:
            return "The file does not contain time dependent activities", 400
    else:
        return "No files of allowed types", 400

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)