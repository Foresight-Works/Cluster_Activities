from dev.pipeline.service.cluster_service5.setup import *
app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

start = time.time()
transformer_model = SentenceTransformer(transformer_model)
duration.append(['model_upload', round(time.time()-start, 2)])

# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def pipeline():
    # Data
    zipped_files = request.files.get('file', '')
    zipped_files.save(data_path)
    zipped_object = ZipFile(data_path, "r")
    file_names = zipped_object.namelist()
    if os.path.exists(data_file):
        os.remove(data_file)

    print('file_names:', file_names)
    files = {}
    if file_names:
        for file_name in file_names:
            if allowed_file(file_name):
                print(f'allowing file {file_name}')
                print('===={f}===='.format(f=file_name))
                file_posted = zipped_object.read(file_name).decode()
                print(type(file_posted))
                files[file_name] = file_posted

        if files:
            start = time.time()
            print('===parsing the graphml files===')
            projects = graphml_to_nodes(files)
            names, ids = list(projects[names_col]), list(projects[ids_col])
            print('{n} projects tasks(nodes)'.format(n=len(projects)))
            duration.append(['pars_graphml', round(time.time() - start, 2)])

            # Tokens similarity
            print('Calculate Tokens Similarity')
            start = time.time()
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(os.path.join(results_dir, tokens_file), 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))
            tokens_similarity = run_similarity(tokens, 6)
            tokens_similarity.to_pickle(os.path.join(results_dir, 'words_pairs.pkl'))
            duration.append(['words_pairs', round(time.time() - start, 2)])

            # Encode names
            print('Encode activity names')
            start = time.time()
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            ids_embeddings = dict(zip(ids, X))
            np.save(os.path.join(results_dir, 'ids_embeddings.npy'), ids_embeddings)
            duration.append(['encode_names', round(time.time() - start, 2)])

            # Cluster names
            start = time.time()
            n_clusters = int(len(names) * n_clusters_perc / 100)
            model_params['n_clusters'] = n_clusters
            model_conf = model_conf_instance(model_name, model_params)
            clustering = model_conf.fit(X)
            clusters_labels = list(clustering.labels_)
            projects['cluster'] = clusters_labels
            clusters = list(projects['cluster'].unique())
            response, validation_response = build_clusters_response(projects, clusters, tokens_similarity)
            duration.append(['cluster_names', round(time.time() - start, 2)])

            # todo: Evaluate clusters
            clusters_dict = {}
            for cluster in clusters: clusters_dict[cluster] = list(projects[ids_col][projects['cluster'] == cluster])
            scores = evaluate_clusters(clusters_dict, projects, eval_metrics, ids_embeddings=ids_embeddings, scaled=True)
            scores.to_excel(os.path.join(results_dir, 'scores.xlsx'))
            wcss = sum (scores['cluster_ss'])
            print('clustrering score(wcss):', wcss)
            # write wcss to a database

            # Results
            with open(os.path.join(results_dir, "{p}_{n}Clusters_validation_response.json".\
                    format(p=project_name, n=n_clusters)), "w") as outfile:
                outfile.write(response)
            with open(os.path.join(results_dir, "{p}_response.json".format(p=project_name)), "w") as outfile:
                outfile.write(validation_response)

            duration_df = pd.DataFrame(duration, columns=['process', 'processes'])
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


