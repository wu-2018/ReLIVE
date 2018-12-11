from os import mkdir
from os.path import dirname, join, exists
import sys

from flask_cors import CORS
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='/statics')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
CORS(app, supports_credentials=True)

@app.route('/pair_data', methods=['GET'])
def pair_data():
    print(request.args.to_dict()['s'])
    page_s = int(request.args.to_dict()['s'])
    page_e = int(request.args.to_dict()['e'])
    data = pair.iloc[page_s:page_e,:].to_json()
    time.sleep(3)
    return data

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    file_name = 'file_' + secure_filename(f.filename)
    f.save(join(upload_path, file_name))
    return file_name

@app.route('/store', methods=['GET'])
def store():
    sdd = request.args.to_dict()
    print(sdd)
    return "fine."    

#if __name__ == '__main__':
import pandas as pd
base_path = dirname(__file__)
upload_path = join(base_path, 'data/uploads')
if not exists(upload_path):
    mkdir(upload_path)
pair = pd.read_table(base_path+'/data/pairs.tsv')
import time
pairData = pair.iloc[:10,:].to_html()
#port = int(sys.argv[1])
#app.run(host='localhost',port=port)

