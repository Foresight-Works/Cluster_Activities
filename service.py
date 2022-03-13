import os

from setup import *

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir


# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def run_service():
    # Experiment set up
    experiment_id = request.values.get('experiment_id', ' ')
    print('experiment_id:', experiment_id)
    experiment_dir_name = 'experiment_{id}'.format(id=experiment_id)
    min_cluster_size = int(request.values.get('min_cluster_size', ' '))
    print('min_cluster_size:', min_cluster_size)

    experiment_dir = os.path.join(results_dir, experiment_dir_name)
    if experiment_dir_name not in os.listdir(results_dir):
        os.mkdir(experiment_dir)
    runs_dir = os.path.join(experiment_dir, 'runs')
    if 'runs' not in os.listdir(experiment_dir):
        os.mkdir(runs_dir)
    for metric, optimize in metrics_optimize.items():
        posted_value = request.values.get(metric, '')
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
        file_names_str = '|'.join(file_names).rstrip('|').replace('.graphml', '')
        # File name validation
        for file_name in file_names:
            if allowed_file(file_name, config.get('data', 'extensions')):
                print(f'allowing file {file_name}')
                print('===={f}===='.format(f=file_name))
                file_posted = zipped_object.read(file_name).decode(encoding='utf-8-sig')
                format = file_name.split('.')[1]
                if format == 'graphml':
                    parsed_df = parse_graphml(file_posted, headers)
                elif format == 'xer':
                    print('xer format')
                    xer_lines = file_posted.split('\n')
                    with open('tmp_xer.xer', 'w') as f:
                        for line in xer_lines: f.write('{l}\n'.format(l=line))
                    graphml_file = xer_nodes('tmp_xer.xer')
                    graphml_str = open(graphml_file).read()
                    parsed_df = parse_graphml(graphml_str, headers)

                elif format == 'csv':
                    parsed_df = parse_csv(file_posted)
                print('file: {n}, {r} tasks'.format(n=file_name, r=len(parsed_df)))
                projects = projects.append(parsed_df)

        # Projects TDAs
        projects.to_excel('pre_filter.xlsx', index=False)
        print(projects[task_type].head())
        print('task type values:', projects[task_type].unique())
        print(projects[task_type].value_counts())
        projects = projects[projects[task_type].isin(['TT_TASK', 'TT_Task'])]
        projects.to_excel('filtered.xlsx', index=False)
        #projects = projects.replace("", float("NaN")).dropna()
        tasks_count = len(projects)
        print('{n} tdas'.format(n=tasks_count))
        print('projects')
        print(projects.head())
        print(projects.info())
        if len(projects) > 0:
            run_pipeline(projects, experiment_id, experiment_dir, runs_dir, num_files, file_names_str, results_columns, metrics_cols, metrics_optimize, conn)
            return 'Activity names are being clustered'
        else:
            return "The file does not contain time dependent activities", 400
    else:
        return "No files of allowed types", 400

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)

