from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
from flask import send_file
from university.student_data import get_student_id_by_cc
import tempfile
from university.diploma_verification import diploma_verification
app = Flask(__name__)
CORS(app)

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

    diploma_path = os.path.join(r"C:\Users\strik\Documents\GitHub\Blockchain-Python\DiplomaRegistry\Diplomas", f'diploma_{student_id}.pdf')

    if not os.path.exists(diploma_path):
        return jsonify({'error': 'Diploma not found'}), 404

    return send_file(diploma_path, as_attachment=True)


@app.route('/api/diploma-validation', methods=['POST'])
def diploma_validation():
    file = request.files.get('file')
    cc = request.form.get('cc')

    if not file or not cc:
        return jsonify({'valid': False, 'message': 'Missing file or CC'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            file.save(temp.name)
            temp_path = temp.name

        # Call verification function
        is_valid = diploma_verification(temp.name, cc)

        # Delete the file after verification
        os.remove(temp_path)

        if is_valid:
            return jsonify({'valid': True, 'message': 'Diploma is valid'})
        else:
            return jsonify({'valid': False, 'message': 'Diploma verification failed'})

    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
