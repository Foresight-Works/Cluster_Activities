from setup import *
from tokens_similarity1 import *

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir
duration = []

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
            if allowed_file(file_name, config.get('response', 'extensions')):
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

            ### Tokens similarity ###
            print('Calculate Tokens Similarity')
            start = datetime.now()
            tokens = tokenize(names, is_list=True, exclude_stopwords=True, \
                              exclude_numbers=True, exclude_digit_tokens=True)
            with open(os.path.join(results_dir, 'tokens.txt'), 'w') as f:
                for token in tokens: f.write('{t}\n'.format(t=token))
            tokens_similarity = run_similarity(tokens, 6)
            tokens_similarity.to_pickle(os.path.join(results_dir, 'words_pairs.pkl'))
            duration.append(['words_pairs', round((datetime.now() - start).total_seconds(), 2)])
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


