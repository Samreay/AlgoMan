from flask import Flask, request
from pydispatch import dispatcher

from augmentor import Augmentor
from data_store import DataStore
from raw_digest import RawDataDigester

app = Flask(__name__)


@app.route('/api/add_raw_data', methods=['POST'])
def add_raw_data():
    content = request.json
    dispatcher.send("raw_data", data=content)
    return '', 204

if __name__ == '__main__':
    r = RawDataDigester()
    a = Augmentor()
    #d = DataStore()
    app.run(host='0.0.0.0', debug=True)
