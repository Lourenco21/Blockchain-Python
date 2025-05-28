from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
from university.student_data import get_student_id_by_cc
from flask import send_file

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


@app.route('/api/student-id', methods=['GET', 'POST'])
def get_student_id():
    if request.method == 'POST':
        data = request.get_json()
        cc = data.get('cc')
    else:  # GET
        cc = request.args.get('cc')
    if not cc:
        return jsonify({'error': 'Missing CC'}), 400

    students_file = os.path.join(CSV_DIR, 'students.csv')
    student_id = get_student_id_by_cc(cc, csv_path=students_file)
    if student_id:
        return jsonify({'student_id': student_id})
    else:
        return jsonify({'error': 'Student not found'}), 404


@app.route('/api/diploma-pdf')
def diploma_pdf():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    diploma_path = os.path.join(r"C:\Users\User\OneDrive\Documents\GitHub\Blockchain-Python\DiplomaRegistry\Diplomas", f'diploma_{student_id}.pdf')

    if not os.path.exists(diploma_path):
        return jsonify({'error': 'Diploma not found'}), 404

    return send_file(diploma_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
