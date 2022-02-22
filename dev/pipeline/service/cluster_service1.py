from setup import *
app = Flask(Flask.__name__)
print('data_dir:', data_dir)
app.config['UPLOAD_FOLDER'] = data_dir

def allowed_file(filename):
    """ Tests if filetype is an allowed filetype """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse_graphml_file(file_path):

    raw_data = open(file_path).read().split('</node>')
    nodes = [s for s in raw_data if 'node id' in s]
    nodes = [n.lstrip().rstrip() for n in nodes]
    nodes = [n.replace('"', '') for n in nodes]
    # Exclude file header
    nodes = nodes[1:]

    nodes_df = pd.DataFrame()
    for node in nodes:
        node_rows = node.split('\n')
        id = re.findall('=(.*?)>', node_rows[0])[0]
        node_rows = node_rows[1:]
        keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
        values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
        node_df = pd.DataFrame([values], columns = keys)
        nodes_df = nodes_df.append(node_df)
    return nodes_df



@app.route('/clusters', methods=['POST'])
def pipeline():

    # Data
    print('request.method:', request.method)
    file = request.files.get('file', '')
    print('request.files:', request.files)
    if 'file' in request.files and allowed_file(file.filename):
        print(f'allowing file {file.filename}')
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        print('file_path:', file_path)
        status = 'data uploaded'

        raw_data = open(file_path).read().split('</node>')
        nodes = [s for s in raw_data if 'node id' in s]
        nodes = [n.lstrip().rstrip() for n in nodes]
        nodes = [n.replace('"', '') for n in nodes]

        # Exclude file header
        nodes = nodes[1:]

        nodes_df = pd.DataFrame()
        for node in nodes:
            node_rows = node.split('\n')
            id = re.findall('=(.*?)>', node_rows[0])[0]
            node_rows = node_rows[1:]
            keys = ['ID'] + [re.findall('=(.*?)>', n)[0] for n in node_rows]
            values = [id] + [re.findall('>(.*?)<', n)[0] for n in node_rows]
            node_df = pd.DataFrame([values], columns=keys)
            nodes_df = nodes_df.append(node_df)

    else:
        status = 'No file part'
    print('upload status:', status)

    return status


if __name__ == '__main__':
    print(socket.gethostbyname(socket.gethostname()))
    # app.run(host='0.0.0.0')
    app.run(
        host='127.0.0.1',
        port=6001,
        debug=True)

