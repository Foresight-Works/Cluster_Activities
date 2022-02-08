import pandas as pd

from setup import *
app = Flask(Flask.__name__)
print('data_dir:', data_dir)
app.config['UPLOAD_FOLDER'] = data_dir

def allowed_file(filename):
    """ Tests if filetype is an allowed filetype """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse_graphml_file(file_paths):
    '''
    Parse graphml files
    file_paths (list): Paths to the files to parse
    '''
    nodes_df = pd.DataFrame()
    for file_path in file_paths:
        print('file_path:', file_path)
        file_name = re.findall('(\w+)\.graphml', file_path)[0]
        nodes_df = pd.DataFrame()
        raw_data = open(file_path).read().split('</node>')
        print('raw data:', raw_data)
        nodes = [s for s in raw_data if 'node id' in s]
        nodes = [n.lstrip().rstrip() for n in nodes]
        nodes = [n.replace('"', '') for n in nodes]
        # Exclude file header
        nodes = nodes[1:]
        for node in nodes:
            node_rows = node.split('\n')
            id = re.findall('=(.*?)>', node_rows[0])[0]
            node_rows = node_rows[1:]
            keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
            values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
            node_df = pd.DataFrame([values], columns=keys)
            node_df['source_file'] = file_name
            nodes_df = nodes_df.append(node_df)

    return nodes_df


@app.route('/analysis', methods=['POST'])
def pipeline():

    # Data
    print('request.method:', request.method)
    print('request.files:', request.files)
    uploaded_files = request.files.getlist("file")
    print('uploaded_files:')
    print(uploaded_files)
    save_paths = []
    for file_name in data_files_names:
        print('file_name:', file_name)
        key = data_file_name.replace('.graphml', '')
        print('key:', key)
        file = request.files.get(key, '')
        #if file_name in request.files and allowed_file(file.filename):
        #print(f'allowing file {file.filename}')
        print('file.filename:', file.filename)
        filename = secure_filename(file.filename)
        print('secure file.filename:', filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        print('save path:', save_path)
        save_paths.append(save_path)
    if save_paths:
        status = 'data uploaded'
    else:
        status = 'No file part'
    print('upload status:', status)
    nodes_df = parse_graphml_file(save_paths)
    nodes_df.to_excel('nodes_df.xlsx')

    return status



if __name__ == '__main__':
    print(socket.gethostbyname(socket.gethostname()))
    # app.run(host='0.0.0.0')
    app.run(
        host='127.0.0.1',
        port=6001,
        debug=True)

