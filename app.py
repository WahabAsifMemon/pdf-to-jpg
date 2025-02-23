import os
from flask import Flask, request, send_file, render_template, jsonify
from pdf2image import convert_from_path
import zipfile
import io
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
POPPLER_PATH = r'C:\poppler-utils\Library\bin'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        image_files = []
        for i, image in enumerate(images):
            image_filename = f'page_{i + 1}.jpg'
            image_path = os.path.join(OUTPUT_FOLDER, image_filename)
            image.save(image_path, 'JPEG')
            image_files.append(image_filename)
        return jsonify({'images': image_files})

@app.route('/download_all')
def download_all():
    image_files = request.args.get('images').split(',')
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image in image_files:
            zip_file.write(os.path.join(OUTPUT_FOLDER, image), image)
    zip_buffer.seek(0)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    zip_filename = f'images_{timestamp}.zip'
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=zip_filename)

if __name__ == '__main__':
    app.run(debug=True)
