import os

from setup import *

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = data_dir

# Response
@app.route('/cluster_analysis/api/v0.1/clustering', methods=['POST'])
def run_service():
    # Experiment set up
    zipped_files = request.files.get('file', '')
    print('zipped_files:', zipped_files)
    return 'files recieved'

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='127.0.0.1', port=6002)


