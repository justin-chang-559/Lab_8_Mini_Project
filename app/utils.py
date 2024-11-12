import csv
from app import db
from app.models import Course, User, Enrollment
import os

def import_enrollment_data(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print("row",row)
            # Get or create the course
            course_name = row['Class Name'].strip()
            course = Course.query.filter_by(name=course_name).first()
            if not course:
                course = Course(name=course_name, capacity=int(row['Capacity']))
                db.session.add(course)

            # Get or create the teacher
            teacher_name = row['Teacher Name'].strip()
            teacher = User.query.filter_by(username=teacher_name).first()
            if not teacher:
                teacher = User(username=teacher_name, role='teacher')
                db.session.add(teacher)

            # Create enrollments for students and assign grades if available
            student_names = row['Student Name'].split(',')
            grades = row['Grade'].split(',') if row['Grade'] else []

            for index, student_name in enumerate(student_names):
                student_name = student_name.strip()
                if student_name:
                    student = User.query.filter_by(username=student_name).first()
                    if not student:
                        student = User(username=student_name, role='student')
                        db.session.add(student)
                    
                    # Assign grade if it exists for the student
                    grade = float(grades[index].strip()) if index < len(grades) and grades[index].strip() else None
                    enrollment = Enrollment(student_id=student.id, course_id=course.id, grade=grade)
                    db.session.add(enrollment)

    db.session.commit()
