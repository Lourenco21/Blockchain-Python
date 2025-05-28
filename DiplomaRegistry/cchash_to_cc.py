from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_DIR = os.path.join(BASE_DIR, 'university')
os.makedirs(CSV_DIR, exist_ok=True)
CSV_FILE = os.path.join(CSV_DIR, 'cc_hash_map.csv')


@app.route('/api/store-cc', methods=['POST'])
def store_cc():
    data = request.get_json()
    cc = data.get('cc')
    cc_hash = data.get('ccHash')

    if not cc or not cc_hash:
        return jsonify({'error': 'Missing CC or CC hash'}), 400

    already_exists = False
    file_exists = os.path.exists(CSV_FILE)

    if file_exists:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['cc'] == cc or row['cc_hash'] == cc_hash:
                    already_exists = True
                    break

    if already_exists:
        return jsonify({'status': 'already exists'})

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists or os.stat(CSV_FILE).st_size == 0:
            writer.writerow(['cc', 'cc_hash'])
        writer.writerow([cc, cc_hash])

    return jsonify({'status': 'stored'})

# New endpoint to validate diploma PDF
@app.route('/api/validate-diploma', methods=['POST'])
def validate_diploma():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'message': 'Ficheiro não é diploma'}), 400

    try:
        # Read PDF from file stream
        pdf_document = fitz.open(stream=file.read(), filetype='pdf')

        # Extract text from all pages
        text = ""
        for page in pdf_document:
            text += page.get_text()

        pdf_document.close()

        # Validate diploma structure
        is_valid = validate_diploma_structure(text)

        if is_valid:
            return jsonify({'message': 'Diploma Reconhecido'})
        else:
            return jsonify({'message': 'Ficheiro não é diploma'})

    except Exception as e:
        return jsonify({'error': f'Failed to process PDF: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
