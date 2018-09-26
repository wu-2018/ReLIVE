from os.path import dirname

from flask_cors import CORS
from flask import Flask, request, render_template
#from bokeh.client import pull_session
#from bokeh.embed import server_session

app = Flask(__name__, static_folder='static', static_url_path='/statics')
CORS(app, supports_credentials=True)

@app.route('/pair_data', methods=['GET'])
def pair_data():
        print(request.args.to_dict()['s'])
        page_s = int(request.args.to_dict()['s'])
        page_e = int(request.args.to_dict()['e'])
        data = pair.iloc[page_s:page_e,:].to_json()
        time.sleep(3)
        return data

@app.route('/store', methods=['GET'])
def store():
    sdd = request.args.to_dict()
    print(sdd)
    return "fine."    

if __name__ == '__main__':
    import pandas as pd
    dir_ = dirname(__file__)
    pair = pd.read_table(dir_+'/data/pairs.tsv')
    import time
    pairData = pair.iloc[:10,:].to_html()

    app.run(host='localhost',port=8080)

