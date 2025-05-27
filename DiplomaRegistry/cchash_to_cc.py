from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from frontend (like localhost:3000)

# Create full path to CSV file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'university', 'cc_hash_map.csv')

# Ensure 'university' directory exists
os.makedirs(os.path.join(BASE_DIR, 'university'), exist_ok=True)

@app.route('/api/store-cc', methods=['POST'])
def store_cc():
    try:
        data = request.get_json()
        cc = data.get('cc')
        cc_hash = data.get('ccHash')

        if not cc or not cc_hash:
            return jsonify({'error': 'Missing CC or CC hash'}), 400

        # Write to CSV file
        file_exists = os.path.isfile(CSV_FILE)
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['cc', 'cc_hash'])  # header row
            writer.writerow([cc, cc_hash])

        return jsonify({'status': 'stored'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

