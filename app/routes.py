from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Course, Enrollment

def init_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user = User.query.filter_by(username=request.form['username']).first()
            if user and user.check_password(request.form['password']):  # Check password securely
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        if current_user.role == 'student':
            return redirect(url_for('student_courses'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher_classes'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))

    @app.route('/student/courses')
    @login_required
    def student_courses():
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        courses = [e.course for e in enrollments]
        return render_template('student/courses.html', courses=courses)

    @app.route('/student/enroll', methods=['GET', 'POST'])
    @login_required
    def student_enroll():
        # Check if the form is submitted
        if request.method == 'POST':
            course_id = request.form['course_id']
            action = request.form['action']
            course = Course.query.get(course_id)
            
            # Enroll in the course
            if action == 'enroll':
                if course and course.capacity > course.enrollments.count():
                    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
                    db.session.add(enrollment)
                    db.session.commit()
                    flash('Enrolled in the course successfully.')
                else:
                    flash('The course is full.')
            
            # Drop the course
            elif action == 'drop':
                enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
                if enrollment:
                    db.session.delete(enrollment)
                    db.session.commit()
                    flash('Dropped the course successfully.')
            
            return redirect(url_for('student_enroll'))

        # Fetch all courses and check if the student is already enrolled in each
        courses = Course.query.all()
        enrolled_courses = {enrollment.course_id for enrollment in Enrollment.query.filter_by(student_id=current_user.id).all()}

        return render_template('student/enroll.html', courses=courses, enrolled_courses=enrolled_courses)



    @app.route('/teacher/classes')
    @login_required
    def teacher_classes():
        enrollments = Enrollment.query.join(Course).filter_by(name=current_user.username).all()
        return render_template('teacher/classes.html', enrollments=enrollments)

    @app.route('/teacher/students/<course_id>', methods=['GET', 'POST'])
    @login_required
    def teacher_students(course_id):
        course = Course.query.get(course_id)
        if request.method == 'POST':
            for student_id, grade in request.form.items():
                if student_id != 'course_id':
                    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
                    if enrollment:
                        enrollment.grade = grade
                        db.session.commit()
            flash('Grades updated successfully.')
        return render_template('teacher/students.html', course=course)

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            return redirect(url_for('index'))
        users = User.query.all()
        courses = Course.query.all()
        enrollments = Enrollment.query.all()
        return render_template('admin/dashboard.html', users=users, courses=courses, enrollments=enrollments)
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']  # 'student' or 'teacher'
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists.')
                return redirect(url_for('signup'))

            # Create a new user
            new_user = User(username=username, role=role)
            new_user.set_password(password)  # Securely set hashed password
            db.session.add(new_user)
            db.session.commit()

            # Automatically log the user in after signup
            login_user(new_user)
            flash('Account created successfully.')
            return redirect(url_for('index'))
        
        return render_template('signup.html')
