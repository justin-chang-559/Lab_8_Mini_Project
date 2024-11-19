import csv
import os
from app import db
from app.models import Course, User, Enrollment
from werkzeug.security import generate_password_hash

def import_enrollment_data(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get or create the teacher
            teacher_name = row['Teacher Name'].strip()
            teacher = User.query.filter_by(username=teacher_name).first()
            if not teacher:
                teacher = User(
                    username=teacher_name,
                    email=f"{teacher_name.replace(' ', '').lower()}@school.com",  # Generate default email
                    password_hash = generate_password_hash('defaultpassword'),
                    role='teacher'
                )
                db.session.add(teacher)

            # Get or create the course
            course_name = row['Class Name'].strip()
            course = Course.query.filter_by(name=course_name).first()
            if not course:
                course = Course(
                    name=course_name,
                    capacity=int(row['Capacity']),
                    meeting_time=row['Time'].strip(),
                    teacher=teacher
                )
                db.session.add(course)

            # Other enrollment logic...
    db.session.commit()

def create_admin_account():
    # Check if the admin user already exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # Create the admin user with the specified username and password
        admin_password = generate_password_hash('admin123')
        admin_user = User(username='admin', email='admin@example.com', password_hash=admin_password, role='admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin account created: username='admin', password='admin123'")
    else:
        print("Admin account already exists.")