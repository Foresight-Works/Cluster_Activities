import pandas as pd

from setup import *
app = Flask(Flask.__name__)
print('data_dir:', data_dir)
app.config['UPLOAD_FOLDER'] = data_dir

@app.route('/analysis', methods=['POST'])
def pipeline():

    # Data
    print('request.method:', request.method)
    print('request.files:', request.files)
    files = request.files.getlist("file")
    print('uploaded_files:')
    print(files)
    save_paths = []
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
    else:
        status = 'No file part'
    print('upload status:', status)
    nodes_df = parse_graphml_file(save_paths)
    nodes_df.to_excel('nodes_df.xlsx', index=False)

    return status


if __name__ == '__main__':
    print(socket.gethostbyname(socket.gethostname()))
    # app.run(host='0.0.0.0')
    app.run(
        host='127.0.0.1',
        port=6001,
        debug=True)

