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

    # Check if entry already exists
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

    # Write new row
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists or os.stat(CSV_FILE).st_size == 0:
            writer.writerow(['cc', 'cc_hash'])  # header
        writer.writerow([cc, cc_hash])

    return jsonify({'status': 'stored'})

if __name__ == '__main__':
    app.run(debug=True)
