from flask import Flask, jsonify, render_template
from backend import get_current_component_counts

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/components', methods=['GET'])
def components():
    return jsonify(get_current_component_counts())

def run_server():
    app.run(host='0.0.0.0', port=5000)
