from flask import Flask, request, jsonify, send_file
import os
import uuid
import asyncio
from api.youtube import *
from api.transcriptions import *

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
PDF_FOLDER = './static/pdf'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

processing_status = {}
processing_results = {}

client = create_client()

@app.route('/cdn/pdf/<filename>')
def get_pdf(filename):
    pdf_path = f"{PDF_FOLDER}/{filename}"
    try:
        return send_file(pdf_path, mimetype='application/pdf')
    except FileNotFoundError:
        return "File not found", 404


async def start_processing(file_id):
    file_path = f"{UPLOAD_FOLDER}/{file_id}.pdf"
    processing_status[file_id] = "Generating Latex"
    latex = notes_to_latex(client, file_path)
    compile_latex(latex)
    processing_status[file_id] = "Compiling to PDF"
    output_pdf_path = f"{PDF_FOLDER}/{file_id}.pdf"
    encode_pdf(output_pdf_path, 2)
    pdf_link = f"localhost:8888/cdn/pdf/{file_id}.pdf"
    processing_status[file_id] = "Getting YouTube Videos"
    yt_queries = get_youtube_queries(latex)
    videos = []
    for query in yt_queries:
        videos.append(youtube_search(query).pop())
    result = {'pdf': pdf_link, 'videos': videos}
    return result

@app.route('/upload', methods=['POST'])
async def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_FOLDER}/{file_id}.pdf"
    file.save(file_path)

    processing_status[file_id] = 'Processing'
    asyncio.create_task(background_process(file_id))

    return jsonify({'file_id': file_id}), 200


async def background_process(file_id):
    processing_results[file_id] = await start_processing(file_id)
    processing_status[file_id] = 'done'


@app.route('/status', methods=['GET'])
async def check_status():
    file_id = request.args.get('file_id')
    if file_id not in processing_status:
        return jsonify({'error': 'Invalid file_id'}), 404
    if processing_status[file_id] == 'done':
        return jsonify({'status': 'done', 'results': processing_results[file_id]}), 200
    else:
        return jsonify({'status': processing_status[file_id]}), 200


if __name__ == '__main__':
    app.run(debug=True, port=8888)

