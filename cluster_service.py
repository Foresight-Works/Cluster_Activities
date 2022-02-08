import os

from modules.utils import *
from modules.clustering import *
from modules.cluster_names import *
app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
#durations = []
# todo: update upload or pipeline to allow more then one project in the data path

# Response
@app.route('/analysis', methods=['POST'])
def pipeline():
    # Data
    print('request.method:', request.method)
    files_posted = request.files.getlist("file")
    print('uploaded_files:')
    print(files_posted)
    save_paths = []
    # Validate file types
    files = []
    for file in files_posted:
        if allowed_file(file.filename):
            print(f'allowing file {file.filename}')
            files.append(file)

    if files:
        for file in files:
            print('>>file:', file)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            print('save path:', save_path)
            save_paths.append(save_path)
            file.save(save_path)
            print('file.filename:', file.filename)
            # filename = secure_filename(file.filename)
            # print('secure file.filename:', filename)

        if save_paths:
            status = 'data uploaded'
            print('save_paths:')
            for p in save_paths: print(p)

            print('upload status:', status)
            projects = parse_graphml_files(save_paths)
            projects.to_excel('projects.xlsx', index=False)

            names = list(projects[names_col])
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(os.path.join(results_dir, tokens_file), 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))
            tokens_similarity = run_similarity(tokens, 6)
            tokens_similarity.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))
            #Todo integration: transformer_model before pipeline
            transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            model_params['n_clusters'] = int(len(names) * n_clusters_perc / 100)
            model_conf = model_conf_instance(model_name, model_params)
            clustering = model_conf.fit(X)
            clusters_labels = list(clustering.labels_)
            projects['cluster'] = clusters_labels
            clusters = list(projects['cluster'].unique())
            response, validation_response = build_clusters_response(projects, clusters, tokens_similarity)
            with open(os.path.join(results_dir, "{p}_validation_response.json".format(p=project_name)), "w") as outfile:
                outfile.write(response)
            with open(os.path.join(results_dir, "{p}_response.json".format(p=project_name)), "w") as outfile:
                outfile.write(validation_response)
            return response
        else:
            return "Record not found", 400

    else:
        return "No files of allowed types", 400


if __name__ == '__main__':
    print(socket.gethostbyname(socket.gethostname()))
    # app.run(host='0.0.0.0')
    app.run(
        host='127.0.0.1',
        port=6001,
        debug=True)


