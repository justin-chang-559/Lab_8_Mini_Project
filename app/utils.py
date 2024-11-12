import csv
from app import db
from app.models import Course, User, Enrollment
import os

import csv
import os
from app import db
from app.models import Course, User, Enrollment
from werkzeug.security import generate_password_hash

def import_enrollment_data(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
        
    default_password = "defaultpassword"  # Define a default password for new users
    hashed_default_password = generate_password_hash(default_password)  # Hash the default password

    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print("row", row)  # Debugging output to verify row structure

            # Ensure required fields are present
            if not row['Class Name'] or not row['Teacher Name'] or not row['Capacity'] or not row['Student Name']:
                print(f"Skipping incomplete row: {row}")
                continue

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
                teacher_email = f"{teacher_name.replace(' ', '').lower()}@example.com"  # Generate default email
                teacher = User(username=teacher_name, email=teacher_email, password_hash=hashed_default_password, role='teacher')
                db.session.add(teacher)
            elif not teacher.email or not teacher.password_hash:
                # Update existing teacher with default email or password if missing
                if not teacher.email:
                    teacher.email = f"{teacher_name.replace(' ', '').lower()}@example.com"
                if not teacher.password_hash:
                    teacher.password_hash = hashed_default_password

            # Get or create the student
            student_name = row['Student Name'].strip()
            student = User.query.filter_by(username=student_name).first()
            if not student:
                student_email = f"{student_name.replace(' ', '').lower()}@example.com"  # Generate default email
                student = User(username=student_name, email=student_email, password_hash=hashed_default_password, role='student')
                db.session.add(student)
            elif not student.email or not student.password_hash:
                # Update existing student with default email or password if missing
                if not student.email:
                    student.email = f"{student_name.replace(' ', '').lower()}@example.com"
                if not student.password_hash:
                    student.password_hash = hashed_default_password

            # Create an enrollment if it doesn’t already exist
            existing_enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
            if not existing_enrollment:
                grade = float(row['Grade'].strip()) if row['Grade'] else None
                enrollment = Enrollment(student_id=student.id, course_id=course.id, grade=grade)
                db.session.add(enrollment)

    db.session.commit()