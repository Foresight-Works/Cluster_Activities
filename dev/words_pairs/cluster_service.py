from setup import *
from dev.words_pairs.versions.calculate_similarity_performance import *

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

## Language models ##
start = datetime.now()
# Sentences embeddings
# sentences_model = config.get('language_models', 'sentences')
# transformer_model = SentenceTransformer(sentences_model)
# print('Sentences embeddings loaded')

# Tokens embeddings
model_name = config.get('language_models', 'tokens')
tokens_embeddings = api.load("{m}".format(m=model_name))
#duration.append(['model_upload', round((datetime.now() - start).total_seconds(), 2)])
print('Tokens embeddings loaded')

results_dir = './results'
# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def pipeline():
    experiment_id = request.values.get('experiment_id', '{}')

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

            sim_measures = ['charecters']


            ### Tokens similarity ###
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                               exclude_numbers=True, exclude_digit_tokens=True)
            # Strings (lcs)
            # print('Calculate Tokens Similarity')
            # start = datetime.now()
            # with open(os.path.join(results_dir, 'tokens.txt'), 'w') as f:
            #     for token in tokens: f.write('{t}\n'.format(t=token))
            # tokens_similarity = run_similarity(tokens, 6)
            # tokens_similarity.to_pickle(os.path.join(results_dir, 'words_pairs.pkl'))
            # duration.append(['words_pairs', round((datetime.now() - start).total_seconds(), 2)])

            # # Semantic space (embeddings)
            vocab_embeddigs, not_in_vocabulary = filter_embeddings(tokens, tokens_embeddings)
            np.save(os.path.join(results_dir, 'vocab_embeddigs.npy'), vocab_embeddigs)
            print('{} tokens in twitter vocabulary'.format(len(tokens)))
            #results_dir = os.path.join(results_dir, 'similarity')
            with open(os.path.join(results_dir, 'not_in_{m}.txt'.format(m=model_name)), 'w') as f:
                for i in not_in_vocabulary:
                    f.write('{i}\n'.format(i=i))



            response = 'Calculation completed'
            print(response)
            return response
        else:
            return "Record not found", 400
    else:
        return "No files of allowed types", 400

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)


