import os

from setup import *

# Database tables
create_db(db_name, conn)
create_table(table_name, results_columns, data_types, conn)

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

# Language models
start = datetime.now()
sentences_model = config.get('language_models', 'sentences')
transformer_model = SentenceTransformer(sentences_model)
duration.append(['model_upload', round((datetime.now() - start).total_seconds(), 2)])
print('Language model loaded')

# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def pipeline():
    experiment_id = request.values.get('experiment_id', '{}')
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
            print('names sample:', names[:10])
            duration.append(['parse_data', round((datetime.now() - start).total_seconds(), 2)])

            names = list(projects[names_col])
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(tokens_path, 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))

            subprocess.call('python tokens_distances.py', shell=True)
            # Encode names
            print('Encode activity names')
            start = datetime.now()
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            ids_embeddings = dict(zip(ids, X))
            #np.save(os.path.join(results_dir, 'ids_embeddings.npy'), ids_embeddings)
            duration.append(['encode_names', round((datetime.now() - start).total_seconds(), 2)])

            results_rows, clustering_results = [], {}
            for run_id, n_clusters_perc in enumerate(n_clusters_percs):
                run_dir = os.path.join(runs_dir, str(run_id))
                print('run_dir:', run_dir)
                if str(run_id) not in os.listdir(runs_dir):
                    os.mkdir(run_dir)
                n_clusters_perc = float(n_clusters_perc)
                run_start = datetime.now()
                # Cluster activities
                print('Cluster activities')
                start = datetime.now()
                model_params = {}
                model_params['affinity'] = affinity
                clustering_params_write = '_'.join(['{param}|{val}'.format(param=k, val=v) for k, v in model_params.items()])
                n_clusters = int(len(names) * n_clusters_perc / 100)
                model_params['n_clusters'] = n_clusters
                model_conf = model_conf_instance(model_name, model_params)
                clustering = model_conf.fit(X)
                clusters_labels = list(clustering.labels_)
                projects['cluster'] = clusters_labels
                clusters = list(projects['cluster'].unique())
                clustering_result, clusters_namesIDs = build_result(projects, clusters, names_col, ids_col)
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
                scores.to_excel(os.path.join(results_dir, 'scores.xlsx'), index=False)
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
                run_start = run_start.strftime("%d/%m/%Y %H:%M:%S")
                run_end = run_end.strftime("%d/%m/%Y %H:%M:%S")
                print("end time =", run_end)

                # Clusters stats
                tasks_per_cluster = [len(v) for k, v in clusters_dict.items()]
                mean_tpc = round(np.mean(tasks_per_cluster), 2)
                median_tpc = round(np.median(tasks_per_cluster), 2)
                min_tpc, max_tpc = np.min(tasks_per_cluster), np.max(tasks_per_cluster)
                min_max_tpc = max_tpc-min_tpc
                # Results
                results_row = [run_id, file_names, project, customer,\
                               num_files, run_start, run_end, run_duration,\
                               tasks_count, sentences_model, model_name, clustering_params_write, \
                               n_clusters_perc, n_clusters, ave_std,\
                               mean_tpc, median_tpc, min_tpc, max_tpc,\
                               min_max_tpc, wcss, bcss, ch_index, db_index, silhouette, words_pairs_score]
                print('results columns count=', len(results_cols_types))
                print('results values count=', len(results_row))

                # Keep the clustering results if the smallest cluster is larger than the minimal cluster size
                if min_tpc >= min_cluster_size:
                    results_rows.append(results_row)
                insert_into_table(table_name, results_columns, results_row, conn)

                clusters_file = '{tc}Tasks_{nc}Clusters.json'.format(tc=tasks_count, nc=n_clusters)
                #with open(os.path.join(results_dir, clusters_file), "w") as outfile:
                #    outfile.write(validation_response)

            metrics_df = pd.DataFrame(results_rows, columns=results_columns)
            print('metrics_df')
            print(metrics_df)
            metrics_df = metrics_df[['run_id']+metrics_cols]
            print('metrics_df')
            print(metrics_df)
            # Select response by voting
            best_score_run_id = vote(metrics_df, metrics_optimize)
            print('best_score_run_id:', best_score_run_id)
            clustering_result = clustering_results[best_score_run_id]
            clustering_result = {best_score_run_id: clustering_result}
            np.save(os.path.join(results_dir, 'clustering_result.npy'), clustering_result)
            # with open(os.path.join(results_dir, "response.json"), "w") as outfile:
            #      outfile.write(response)
            #duration_df = pd.DataFrame(processes, columns=['process', 'processes'])
            #duration_df.to_excel(os.path.join(results_dir, 'duration_{n}_nodes.xlsx'.format(n=len(projects))), index=False)
            print('Calculation completed')
            write_duration('pipeline', pipeline_start)
            response = 'temp response'
            return response
        else:
            return "Record not found", 400
    else:
        return "No files of allowed types", 400

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)


