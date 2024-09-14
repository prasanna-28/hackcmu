import os
from dotenv import load_dotenv
import googleapiclient.discovery
from flask import Flask, request, jsonify
from api.youtube import *

load_dotenv()

app = Flask(__name__)


@app.route('/youtube/search', methods=['GET'])
def search():
    query = request.args.get('query')
    max_results = request.args.get('max_results', default=5, type=int)

    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    try:
        results = youtube_search(query, max_results)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

