import csv
from fpdf import FPDF
import os
from fpdf.enums import XPos, YPos

def load_student(student_id):
    with open('students.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['student_id']) == student_id:
                return {
                    'name': row['name'],
                    'nacionality': row['nacionality'],
                    'cc': row['cc'],
                    'course': row['course'],
                    'degree_title': row['degree_title'],
                    'degree': row['degree'],
                    'final_grade': row['final_grade'],
                    'date_issued': row['date_issued'],
                    'date_final': row['date_final']
                }
    return None


def load_courses(student_id):
    courses = []
    with open('courses.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['student_id']) == student_id:
                courses.append({
                    'course_name': row['course_name'],
                    'year': row['year'],
                    'credits': row['credits'],
                    'grade': row['grade']
                })
    return courses


def calculate_total_credits(courses):
    return sum(int(course['credits']) for course in courses)


def generate_diploma_text(student_data, total_credits):
    return (
        f"Portador do Bilhete de Identidade / Cartão de Cidadão n.º {student_data['cc']}, "
        f"de nacionalidade {student_data['nacionality']}, concluiu todas as unidades curriculares "
        f"que integram o plano de estudos do curso de Licenciatura em {student_data['course']} "
        f"(ver especificação no verso), aos {student_data['date_final']}, tendo obtido {total_credits} créditos, "
        f"pelo que, em conformidade com as disposições legais em vigor, lhe mandei passar o presente diploma, "
        f"conferindo-lhe o grau de {student_data['degree_title']} em {student_data['course']} "
        f"com a classificação final de {student_data['final_grade']} valores."
    )


class DiplomaPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 12)
        self.cell(0, 10, "ISCTE - Instituto Universitário de Lisboa",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)

    def add_diploma_page(self, student_data, diploma_text, student_id):
        self.add_page()

        self.set_font("Helvetica", '', 10)
        self.cell(0, 10, f"Estudante n.º Student nr. {student_id}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 10, f"N.º de Registo Document nr. 2024/XXXX",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("Helvetica", 'B', 16)
        self.ln(10)
        self.cell(0, 10, "DIPLOMA",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.cell(0, 10, student_data['degree'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")  # degree now used here
        self.set_font("Helvetica", '', 10)
        self.cell(0, 10, "(1.º ciclo 1st cycle)",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

        self.ln(10)
        self.set_font("Helvetica", 'B', 20)
        self.cell(0, 12, student_data['name'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)

        self.set_font("Helvetica", '', 12)
        self.multi_cell(0, 8, diploma_text, align='J')

        self.ln(10)
        self.cell(0, 10, "Lisboa, " + student_data['date_issued'],
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)
        self.cell(80, 10, "_________________________",
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(30, 10, "",
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(80, 10, "_________________________",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(80, 10, "A Diretora dos Serviços de Gestão do Ensino",
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(30, 10, "",
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(80, 10, "Director of Academic Services",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_courses_page(self, courses):
        self.add_page()
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "Unidade Curricular / Course Units",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(5)

        self.set_font("Helvetica", 'B', 9)
        self.cell(90, 6, "Unidade Curricular", 1)
        self.cell(30, 6, "Ano Letivo", 1)
        self.cell(30, 6, "Créditos", 1)
        self.cell(30, 6, "Classificação", 1)
        self.ln()

        self.set_font("Helvetica", '', 8)
        for course in courses:
            self.cell(90, 6, course['course_name'], 1)
            self.cell(30, 6, course['year'], 1)
            self.cell(30, 6, str(course['credits']), 1)
            self.cell(30, 6, str(course['grade']), 1)
            self.ln()


def generate_diploma_by_id(student_id):
    student_data = load_student(student_id)
    if not student_data:
        print(f"No data found for student ID {student_id}.")
        return None

    student_courses = load_courses(student_id)
    if not student_courses:
        print(f"No courses found for student ID {student_id}.")
        return None

    total_credits = calculate_total_credits(student_courses)
    diploma_text = generate_diploma_text(student_data, total_credits)

    pdf = DiplomaPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_diploma_page(student_data, diploma_text, student_id)
    pdf.add_courses_page(student_courses)

    # Make sure output folder exists
    output_dir = r"C:\Users\strik\Desktop\Blockchain\Diplomas"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"diploma_{student_id}.pdf")
    pdf.output(output_path)

    print(f"Diploma saved to: {output_path}")
    return output_path



if __name__ == "__main__":
    student_id = 104750
    student_id2 = 105122
    print(f"student_id: {student_id} (type: {type(student_id)})")
    generate_diploma_by_id(student_id)
    generate_diploma_by_id(student_id2)
