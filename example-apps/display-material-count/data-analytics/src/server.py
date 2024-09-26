from flask import Flask, jsonify
from backend import get_component_counts

app = Flask(__name__)

@app.route('/api/v1/component-counts', methods=['GET'])
def component_counts():
    return jsonify(get_component_counts())

def run_server():
    app.run()