from setup import *

# Database tables
create_db(db_name, conn)
create_table(table_name, results_columns, data_types, conn)

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

# Language model
start = datetime.now()
language_model = config.get('language_model', 'name')
transformer_model = SentenceTransformer(language_model)
duration.append(['model_upload', round((datetime.now() - start).total_seconds(), 2)])
print('Language model loaded')

# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def pipeline():

    n_clusters_perc = float(request.values.get('n_clusters_perc', '{}'))
    print('n_clusters_perc:', n_clusters_perc)
    run_start = request.values.get('run_start', '{}')
    print("start time =", run_start)
    run_start = datetime.strptime(run_start, '%d/%m/%Y %H:%M:%S')

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

        # Parse data files
        if files:
            file_names = '|'.join(list(files.keys())).rstrip('|').replace('.graphml', '')
            print('file_names:', file_names)
            num_files = len(files)
            print('parsing {n} files'.format(n=num_files))
            start = datetime.now()
            print('===parsing the data files===')
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

            # Tokens similarity
            print('Calculate Tokens Similarity')
            start = datetime.now()
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(os.path.join(results_dir, 'tokens.txt'), 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))
            tokens_similarity = run_similarity(tokens, 6)
            tokens_similarity.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))
            duration.append(['tokens_similarity', round((datetime.now() - start).total_seconds(), 2)])

            # Encode names
            print('Encode activity names')
            start = datetime.now()
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            ids_embeddings = dict(zip(ids, X))
            #np.save(os.path.join(results_dir, 'ids_embeddings.npy'), ids_embeddings)
            duration.append(['encode_names', round((datetime.now() - start).total_seconds(), 2)])

            # Cluster names
            print('Cluster names')
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
            response, validation_response = build_clusters_response(projects, clusters, tokens_similarity, names_col, ids_col)
            duration.append(['cluster_names', round((datetime.now() - start).total_seconds(), 2)])

            # Evaluation
            clusters_dict = {}
            for cluster in clusters: clusters_dict[cluster] = list(projects[ids_col][projects['cluster'] == cluster])

            # SOS, Calinski-Harabasz index
            bcss, wcss, ch_index, scores = calinski_harabasz_ch_index_sklearn(clusters_dict, ids_embeddings)
            print('distances scores: wcss={w} | bcss={b} |ch_index={ch}'.format(w=wcss, b=bcss, ch=ch_index))
            print('scores')
            print(scores.head())
            print(scores.info())

            # Davies-Bouldin Index
            db_index = davies_bouldin_score(X, clusters_labels)
            db_index = round(db_index, 2)

            # Silhouette Index
            silhouette = metrics.silhouette_score(X, clusters_labels, metric='euclidean')
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

            run_duration = round((datetime.now() - start).total_seconds(), 2)
            run_end = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print("end time =", run_end)

            # Clusters stats
            tasks_per_cluster = [len(v) for k, v in clusters_dict.items()]
            tasks_per_cluster_mean = round(np.mean(tasks_per_cluster), 2)
            tasks_per_cluster_median = round(np.median(tasks_per_cluster), 2)

            # Results
            results_row = [file_names, project, customer, num_files, run_start, run_end, run_duration, tasks_count, \
                           language_model, model_name, clustering_params_write, \
                           n_clusters_perc, n_clusters, tasks_per_cluster_mean, tasks_per_cluster_median,\
                           wcss, bcss, ch_index, db_index, silhouette, ave_std]
            print('results columns count=', len(results_cols_types))
            print('results values count=', len(results_row))

            insert_into_table(table_name, results_columns, results_row, conn)

            clusters_file = '{tc}Tasks_{nc}Clusters.json'.format(tc=tasks_count, nc=n_clusters)
            with open(os.path.join(results_dir, clusters_file), "w") as outfile:
                outfile.write(validation_response)
            # with open(os.path.join(results_dir, "{rn}Response.json".format(rn=run_name)), "w") as outfile:
            #     outfile.write(response)

            duration_df = pd.DataFrame(duration, columns=['process', 'duration'])
            duration_df.to_excel(os.path.join(results_dir, 'duration_{n}_nodes.xlsx'.format(n=len(projects))), index=False)
            print('Calculation completed')
            return response
        else:
            return "Record not found", 400
    else:
        return "No files of allowed types", 400

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)


