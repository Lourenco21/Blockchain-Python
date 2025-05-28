import os
import csv
from datetime import datetime

def get_student_id_by_cc(cc: str, csv_path='students.csv'):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['cc'] == cc:
                return row.get('student_id')
    return None

def check_student_status(cc: str, csv_path='students.csv'):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['cc'] == cc:
                date_final_str = row.get('date_final', '').strip()  # Remove espaços extras
                if not date_final_str:  # Se estiver vazio, considera inelegível
                    return False, "Estudante ainda não concluiu o curso"
                try:
                    date_final = datetime.strptime(date_final_str, '%Y-%m-%d').date()
                except ValueError:
                    return False, f"Formato inválido da data final: {date_final_str}"
                if date_final <= datetime.today().date():
                    return True, "Estudante elegível"
        return False, "Estudante não encontrado na base de dados"


def get_cc_by_hash(cc_hash, csv_path='cc_hash_map.csv'):
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('cc_hash') == cc_hash:
                    return row.get('cc')

    except FileNotFoundError:
        print(f"CSV file not found at {csv_path}")
    except Exception as e:
        print(f"Error reading CSV: {e}")

    return None

def remove_student_by_hash(student_hash_hex, csv_filepath='cc_hash_map.csv'):
    temp_filepath = 'students_temp.csv'
    removed = False

    with open(csv_filepath, 'r', newline='', encoding='utf-8') as infile, \
            open(temp_filepath, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # row['cchash'] contains the student hash in your CSV
            if row['cc_hash'].lower() != student_hash_hex.lower():
                writer.writerow(row)
            else:
                removed = True

    if removed:
        os.replace(temp_filepath, csv_filepath)
        print(f"✅ Removed student with hash {student_hash_hex} from CSV.")
    else:
        os.remove(temp_filepath)
        print(f"⚠️ Student with hash {student_hash_hex} not found in CSV.")