from setup import *

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []


# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def pipeline():

    # Experiment set up
    experiment_id = request.values.get('experiment_id', ' ')
    # print('experiment_id:', experiment_id)
    experiment_dir_name = 'experiment_{id}'.format(id=experiment_id)
    # posted_min_cluster_size = request.values.get('min_cluster_size', ' ')
    # if posted_min_cluster_size != ' ':
    #     min_cluster_size = int(posted_min_cluster_size)
    print('min_cluster_size:', min_cluster_size)

    ## Language models
    print('Loading language model')
    start = datetime.now()
    sentences_model = config.get('language_models', 'sentences')
    if sentences_model in os.listdir(models_dir):
        transformer_model = SentenceTransformer(os.listdir(models_dir, sentences_model))
    else:
        transformer_model = SentenceTransformer(sentences_model)
        transformer_model.save(models_dir)

    duration.append(['model_upload', round((datetime.now() - start).total_seconds(), 2)])
    print('min_cluster_size:', min_cluster_size)

    experiment_dir = os.path.join(results_dir, experiment_dir_name)
    if experiment_dir_name not in os.listdir(results_dir):
        os.mkdir(experiment_dir)
    runs_dir = os.path.join(experiment_dir, 'runs')
    if 'runs' not in os.listdir(experiment_dir):
        os.mkdir(runs_dir)
    for metric, optimize in metrics_optimize.items():
        posted_value = request.values.get(metric, '')
        if posted_value:
            metrics_optimize[metric] = (metrics_optimize[metric][0], int(posted_value))
    print('metrics optimized:', metrics_optimize)

    pipeline_start = time.time()
    # Data
    zipped_files = request.files.get('file', '')
    zipped_files.save('temp.zip')
    zipped_object = ZipFile('temp.zip', "r")
    if 'temp.zip' in os.listdir(): os.remove('temp.zip')
    file_names = zipped_object.namelist()

    print('file_names:', file_names)
    files = {}
    if file_names:
        # File name validation
        for file_name in file_names:
            if allowed_file(file_name, config.get('data', 'extensions')):
                print(f'allowing file {file_name}')
                print('===={f}===='.format(f=file_name))
                file_posted = zipped_object.read(file_name).decode(encoding='utf-8-sig')
                #data_str = open('SIME_DARBY_TASKS.csv', encoding='utf-8-sig').read()
                print(type(file_posted))
                files[file_name] = file_posted

        # Parse response files
        if files:
            file_names = '|'.join(list(files.keys())).rstrip('|').replace('.graphml', '')
            print('file_names:', file_names)
            num_files = len(files)
            print('parsing {n} files'.format(n=num_files))
            start = datetime.now()
            print('===parsing the response files===')
            projects = parse_files(files, data_cols, data_format)
            print('{n} tasks'.format(n=len(projects)))
            projects = projects[projects[task_type] == 'TT_Task']
            projects = projects.replace("", float("NaN")).dropna()
            tasks_count = len(projects)
            print('{n} tdas'.format(n=tasks_count))
            print(projects.info())
            projects.to_excel(os.path.join(results_dir, 'projects.xlsx'), index=False)
            names, ids = list(projects[names_col]), list(projects[ids_col])
            print('cluster_key sample:', names[:10])
            duration.append(['parse_data', round((datetime.now() - start).total_seconds(), 2)])

            names = list(projects[names_col])
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(tokens_path, 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))

            subprocess.call('python tokens_distances.py', shell=True)
            # Encode cluster_key
            print('Encode activity cluster_key')
            start = datetime.now()
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            ids_embeddings = dict(zip(ids, X))
            #np.save(os.path.join(results_dir, 'ids_embeddings.npy'), ids_embeddings)
            duration.append(['encode_names', round((datetime.now() - start).total_seconds(), 2)])

            results_rows, clustering_results = [], {}

            # Number of cluster per run
            n_clusters_posted = int(request.values.get('num_clusters', '1'))
            print('n_clusters_posted:', n_clusters_posted)
            if n_clusters_posted > 1:
                n_clusters_runs = [n_clusters_posted]
            else:
                n_clusters_runs = [int(len(names) * n_clusters_perc/100) for n_clusters_perc in n_clusters_percs]
                n_clusters_runs = [n for n in n_clusters_runs if n>1]
            print('n_clusters runs:', n_clusters_runs)
            print('(tasks_count / 2):', (tasks_count / 2))
            if n_clusters_posted > (tasks_count / 2):
                print('n_clusters_posted > (tasks_count / 2)')
                return 'The number of clusters posted ({nc}) is in the range of the tasks count ({tc}).\n \
                           Re-run the application with a smaller number of clusters.'\
                    .format(nc=n_clusters_posted, tc=tasks_count)
            else:
                for run_id, n_clusters in enumerate(n_clusters_runs):
                    run_id += 1
                    run_dir = os.path.join(runs_dir, str(run_id))
                    print('run_dir:', run_dir)
                    if str(run_id) not in os.listdir(runs_dir):
                        os.mkdir(run_dir)
                    run_start = datetime.now()
                    # Cluster activities
                    print('Cluster activities')
                    start = datetime.now()
                    model_params = {}
                    model_params['affinity'] = affinity
                    clustering_params_write = '_'.join(['{param}|{val}'.format(param=k, val=v) for k, v in model_params.items()])
                    model_params['n_clusters'] = n_clusters
                    model_conf = model_conf_instance(model_name, model_params)
                    clustering = model_conf.fit(X)
                    clusters_labels = list(clustering.labels_)
                    projects['cluster'] = clusters_labels
                    clusters = list(projects['cluster'].unique())
                    clustering_result, clusters_namesIDs = build_result(projects, clusters, names_col, ids_col)
                    np.save(os.path.join(run_dir, 'clusters_namesIDs.npy'), clusters_namesIDs)
                    clustering_results[run_id] = clustering_result
                    duration.append(['cluster_names', round((datetime.now() - start).total_seconds(), 2)])

                    # Evaluation
                    clusters_dict = {}
                    for cluster in clusters: clusters_dict[cluster] = list(projects[ids_col][projects['cluster'] == cluster])

                    # SOS, Calinski-Harabasz index
                    bcss, wcss, ch_index, scores = ch_index_sklearn(clusters_dict, ids_embeddings)
                    print('distances scores: wcss={w} | bcss={b} |ch_index={ch}'.format(w=wcss, b=bcss, ch=ch_index))
                    print('scores')
                    print(scores.head())
                    print(scores.info())

                    # Davies-Bouldin Index
                    db_index = davies_bouldin_score(X, clusters_labels)
                    db_index = round(db_index, 2)

                    # Silhouette Index
                    silhouette = silhouette_score(X, clusters_labels, metric='euclidean')
                    silhouette = round(silhouette, 2)

                    # Duration STD
                    std_scores = clusters_duration_std(clusters_dict, projects)
                    print('std_scores')
                    print(std_scores.head())
                    print(std_scores.info())
                    scores = pd.merge(scores, std_scores, on='key')
                    ave_std = round(sum(scores['duration_std'])/n_clusters, 2)
                    print('average clusters standard deviation:', ave_std)

                    # Words-Pairs
                    references_dir = os.path.join(run_dir, 'references')
                    if 'references' not in os.listdir(run_dir):
                        os.mkdir(references_dir)
                    reference_dictionaries(clustering_result, references_dir)
                    subprocess.call('python words_pairs.py {path}'.format(path=references_dir), shell=True)
                    words_pairs_score = open(os.path.join(results_dir, 'words_pairs_score.txt')).read().split('\n')[0]
                    print('words_pairs_score:', words_pairs_score)

                    run_end = datetime.now()
                    run_duration = round((run_end - run_start).total_seconds(), 2)
                    #run_start = "'{t}'".format(t=run_start.strftime("%d/%m/%Y %H:%M:%S"))
                    #run_end = "'{t}'".format(t=run_end.strftime("%d/%m/%Y %H:%M:%S"))
                    run_start = run_start.strftime("%d/%m/%Y %H:%M:%S")
                    run_end = run_end.strftime("%d/%m/%Y %H:%M:%S")

                    print("end time =", run_end, type(run_end))

                    # Clusters stats
                    tasks_per_cluster = [len(v) for k, v in clusters_dict.items()]
                    mean_tpc = round(np.mean(tasks_per_cluster), 2)
                    median_tpc = round(np.median(tasks_per_cluster), 2)
                    min_tpc, max_tpc = np.min(tasks_per_cluster), np.max(tasks_per_cluster)
                    min_max_tpc = max_tpc-min_tpc

                    # Results
                    results_row = [experiment_id, run_id, file_names, project, customer,\
                                   num_files, run_start, run_end, run_duration,\
                                   tasks_count, sentences_model, model_name, clustering_params_write, \
                                   n_clusters, ave_std,\
                                   mean_tpc, median_tpc, min_tpc, max_tpc,\
                                   min_max_tpc, wcss, bcss, ch_index, db_index, silhouette, words_pairs_score]
                    results_row = [str(i) for i in results_row]
                    print('results columns count=', len(results_cols_types))
                    print('results values count=', len(results_row))

                    # Keep the clustering results if the smallest cluster is larger than the minimal cluster size
                    min_tpc = int(min_tpc)
                    if min_tpc >= min_cluster_size:
                        results_rows.append(results_row)
                    statement = insert_into_table_statement(table_name, results_columns, results_row)
                    print('insert into statement:', statement)
                    c.execute(statement)
                    conn.commit()

                scores = pd.DataFrame(results_rows, columns=results_columns)
                print('scores')
                print(scores)
                # Vote on results
                if len(scores) == 0:
                    print('len(scores) == 0')
                    return 'No clustering result produced the desired minimal clusters level'
                else:
                    scaled_scores = scale_df(scores[metrics_cols])
                    scaled_scores.to_excel(os.path.join(experiment_dir, 'scaled_scores.xlsx'), index=False)
                    print('scaled_scores')
                    print(scaled_scores)
                    # If the user did not specify a desired run to provide as a response, deliver the run with the highest score
                    response_run_id = vote(scaled_scores, metrics_cols, metrics_optimize)
                    # Check point: Selected_run_id in run ids
                    print('response_run_id:', response_run_id)
                    clustering_result = clustering_results[response_run_id]
                    clustering_result = {response_run_id: clustering_result}
                    np.save(os.path.join(results_dir, 'clustering_result.npy'), clustering_result)
                    print('Calculation completed')

                    # Name clusters and build results
                    subprocess.call('python build_response.py', shell=True)
                    if response_type == 'cluster_key':
                        dict_file_name = 'named_clusters.npy'
                    else: dict_file_name = 'named_clusters_ids.npy'
                    response_dict = np.load(os.path.join(results_dir, dict_file_name), allow_pickle=True)[()]
                    np.save('response.npy', response_dict)
                    response = json.dumps(response_dict, indent=4)
                    with open('../../../response.json', 'w') as f:
                        json.dump(response, f)
                    write_duration('pipeline', pipeline_start)
                    #message = 'Hello World!'
                    channel = connection.channel()
                    channel.exchange_declare(exchange=exchange_name, durable=True, exchange_type='direct')
                    channel.queue_declare(queue=queue_name)
                    channel.basic_publish(exchange='', routing_key=queue_name, body=response)
                    print(" [x] Sent %r:%r" % (queue_name, response))
                    connection.close()
                    #return response
        else:
            return "Record not found", 400
    else:
        return "No files of allowed types", 400

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)
