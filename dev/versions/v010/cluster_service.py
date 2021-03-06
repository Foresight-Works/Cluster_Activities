from setup import *
app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

pipeline_start = time.time()
transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
duration.append(['model_upload', round(time.time()-pipeline_start, 2)])

# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def pipeline():
    # Data
    zipped_files = request.files.get('file', '')
    zipped_files.save(data_path)
    zipped_object = ZipFile(data_path, "r")
    file_names = zipped_object.namelist()
    if os.path.exists(data_path):
        os.remove(data_path)

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
            print('{n} projects tasks(nodes)'.format(n=len(projects)))
            duration.append(['pars_graphml', round(time.time() - start, 2)])

            # Tokens similarity
            print('Calculate Tokens Similarity')
            start = time.time()
            names = list(projects[names_col])
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(os.path.join(results_dir, tokens_file), 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))
            tokens_similarity = run_similarity(tokens, 6)
            tokens_similarity.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))
            duration.append(['tokens_similarity', round(time.time() - start, 2)])

            # Encode cluster_key
            print('Encode activity cluster_key')
            start = time.time()
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            duration.append(['encode_names', round(time.time() - start, 2)])

            # Cluster cluster_key
            start = time.time()
            n_clusters = int(len(names) * n_clusters_perc / 100)
            model_params['n_clusters'] = n_clusters
            model_conf = model_conf_instance(model_name, model_params)
            clustering = model_conf.fit(X)
            clusters_labels = list(clustering.labels_)
            projects['cluster'] = clusters_labels
            clusters = list(projects['cluster'].unique())
            duration.append(['cluster_names', round(time.time() - start, 2)])

            # Clusters
            response, validation_response = build_clusters_response(projects, clusters, tokens_similarity)
            with open(os.path.join(results_dir, "{p}_{n}Clusters_validation_response.json".\
                    format(p=project_name, n=n_clusters)), "w") as outfile:
                outfile.write(response)
            with open(os.path.join(results_dir, "{p}_response.json".format(p=project_name)), "w") as outfile:
                outfile.write(validation_response)

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


