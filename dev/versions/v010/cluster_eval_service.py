import os
import time

import pandas as pd

from modules.utils import *
from modules.clustering import *
from modules.cluster_names import *
app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

start = time.time()
transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
duration.append(['model_upload', round(time.time()-start, 2)])

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
        start = time.time()
        for file in files:
            print('>>file:', file)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            print('save path:', save_path)
            save_paths.append(save_path)
            file.save(save_path)
            print('file.filename:', file.filename)
        duration.append(['files_upload', round(time.time() - start, 2)])

        if save_paths:
            status = 'data uploaded'
            print('save_paths:')
            for p in save_paths: print(p)
            print('upload status:', status)
            projects = parse_graphml_files(save_paths)
            projects.to_excel(os.path.join(results_dir, 'projects.xlsx'), index=False)
            names, ids = list(projects[names_col]), list(projects[ids_col])

            # Tokens similarity
            start = time.time()
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(os.path.join(results_dir, tokens_file), 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))
            tokens_similarity = run_similarity(tokens, 6)
            tokens_similarity.to_pickle(os.path.join(results_dir, 'tokens_similarity.pkl'))
            duration.append(['tokens_similarity', round(time.time() - start, 2)])

            # Encode cluster_key
            start = time.time()
            names_embeddings = transformer_model.encode(names, convert_to_tensor=True)
            X = np.array(names_embeddings)
            ids_embeddings = dict(zip(ids, X))
            print('saving encoding', type(ids_embeddings))
            np.save(os.path.join(results_dir, 'ids_embeddings.npy'), ids_embeddings)
            duration.append(['encode_names', round(time.time() - start, 2)])

            # Cluster cluster_key
            start = time.time()
            n_clusters = int(len(names) * n_clusters_perc / 100)
            model_params['n_clusters'] = n_clusters
            model_conf = model_conf_instance(model_name, model_params)
            clustering = model_conf.fit(X)
            clusters_labels = list(clustering.labels_)
            projects['cluster'] = clusters_labels
            duration.append(['cluster_names', round(time.time() - start, 2)])

            # Clusters
            clusters = list(projects['cluster'].unique())
            response, validation_response = build_clusters_response(projects, clusters, tokens_similarity)
            with open(os.path.join(results_dir, "{p}_{n}Clusters_validation_response.json".\
                    format(p=project_name, n=n_clusters)), "w") as outfile:
                outfile.write(response)
            with open(os.path.join(results_dir, "{p}_response.json".format(p=project_name)), "w") as outfile:
                outfile.write(validation_response)

            ## Clusters evaluation
            # Clusters Compactness score (WCSS)

            # Durations STDs Scores

            duration_df = pd.DataFrame(duration, columns=['process', 'duration'])
            duration_df.to_excel(os.path.join(results_dir, 'duration_{n}_nodes.xlsx'.format(n=len(projects))), index=False)
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


