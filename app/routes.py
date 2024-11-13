from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Course, Enrollment
from flask import render_template, flash, redirect, url_for, request
from app.models import User, Course, Enrollment
from werkzeug.security import generate_password_hash
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
        # Only show courses where the logged-in user is the teacher
        courses = Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher/classes.html', courses=courses)

    @app.route('/teacher/students/<int:course_id>', methods=['GET', 'POST'])
    @login_required
    def teacher_students(course_id):
        # Ensure the course is taught by the current teacher
        course = Course.query.filter_by(id=course_id, teacher_id=current_user.id).first_or_404()

        if request.method == 'POST':
            # Update grades for students in the course
            for student_id, grade in request.form.items():
                if student_id != 'course_id':
                    enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
                    if enrollment:
                        enrollment.grade = float(grade)
                        db.session.commit()
            flash('Grades updated successfully.')
            return redirect(url_for('teacher_students', course_id=course_id))

        # Fetch all students enrolled in the course
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        return render_template('teacher/students.html', course=course, enrollments=enrollments)


    # Helper function to check if the user is an admin
    def admin_required():
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("You don't have permission to access this page.")
            return redirect(url_for('index'))

    ### ADMIN DASHBOARD ###
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if admin_required(): return admin_required()
        users = User.query.all()
        courses = Course.query.all()
        enrollments = Enrollment.query.all()
        return render_template('admin/dashboard.html', users=users, courses=courses, enrollments=enrollments)


    ### USER ROUTES ###

    # List all users
    @app.route('/admin/users')
    @login_required
    def admin_users():
        if admin_required(): return admin_required()
        users = User.query.all()
        return render_template('admin/users.html', users=users)

    # Create a new user
    @app.route('/admin/users/new', methods=['GET', 'POST'])
    @login_required
    def admin_new_user():
        if admin_required(): return admin_required()
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            role = request.form['role']
            password_hash = generate_password_hash(request.form['password'])

            new_user = User(username=username, email=email, password_hash=password_hash, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully.')
            return redirect(url_for('admin_users'))
        return render_template('admin/new_user.html')

    # Edit a user
    @app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_user(user_id):
        if admin_required(): return admin_required()
        user = User.query.get_or_404(user_id)
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            user.role = request.form['role']
            db.session.commit()
            flash('User updated successfully.')
            return redirect(url_for('admin_users'))
        return render_template('admin/edit_user.html', user=user)

    # Delete a user
    @app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
    @login_required
    def admin_delete_user(user_id):
        if admin_required(): return admin_required()
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.')
        return redirect(url_for('admin_users'))


    ### COURSE ROUTES ###

    # List all courses
    @app.route('/admin/courses')
    @login_required
    def admin_courses():
        if admin_required(): return admin_required()
        courses = Course.query.all()
        return render_template('admin/courses.html', courses=courses)

    # Create a new course
    @app.route('/admin/courses/new', methods=['GET', 'POST'])
    @login_required
    def admin_new_course():
        if admin_required(): return admin_required()
        teachers = User.query.filter_by(role='teacher').all()
        if request.method == 'POST':
            name = request.form['name']
            capacity = int(request.form['capacity'])
            teacher_id = int(request.form['teacher_id'])
            
            new_course = Course(name=name, capacity=capacity, teacher_id=teacher_id)
            db.session.add(new_course)
            db.session.commit()
            flash('Course created successfully.')
            return redirect(url_for('admin_courses'))
        return render_template('admin/new_course.html', teachers=teachers)

    # Edit a course
    @app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_course(course_id):
        if admin_required(): return admin_required()
        course = Course.query.get_or_404(course_id)
        teachers = User.query.filter_by(role='teacher').all()
        if request.method == 'POST':
            course.name = request.form['name']
            course.capacity = int(request.form['capacity'])
            course.teacher_id = int(request.form['teacher_id'])
            db.session.commit()
            flash('Course updated successfully.')
            return redirect(url_for('admin_courses'))
        return render_template('admin/edit_course.html', course=course, teachers=teachers)

    # Delete a course
    @app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
    @login_required
    def admin_delete_course(course_id):
        if admin_required(): return admin_required()
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully.')
        return redirect(url_for('admin_courses'))


    ### ENROLLMENT ROUTES ###

    # List all enrollments
    @app.route('/admin/enrollments')
    @login_required
    def admin_enrollments():
        if admin_required(): return admin_required()
        enrollments = Enrollment.query.all()
        return render_template('admin/enrollments.html', enrollments=enrollments)

    # Create a new enrollment
    @app.route('/admin/enrollments/new', methods=['GET', 'POST'])
    @login_required
    def admin_new_enrollment():
        if admin_required(): return admin_required()
        students = User.query.filter_by(role='student').all()
        courses = Course.query.all()
        if request.method == 'POST':
            student_id = int(request.form['student_id'])
            course_id = int(request.form['course_id'])
            grade = float(request.form['grade']) if request.form['grade'] else None

            new_enrollment = Enrollment(student_id=student_id, course_id=course_id, grade=grade)
            db.session.add(new_enrollment)
            db.session.commit()
            flash('Enrollment created successfully.')
            return redirect(url_for('admin_enrollments'))
        return render_template('admin/new_enrollment.html', students=students, courses=courses)

    # Edit an enrollment
    @app.route('/admin/enrollments/edit/<int:enrollment_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_enrollment(enrollment_id):
        if admin_required(): return admin_required()
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        students = User.query.filter_by(role='student').all()
        courses = Course.query.all()
        if request.method == 'POST':
            enrollment.student_id = int(request.form['student_id'])
            enrollment.course_id = int(request.form['course_id'])
            enrollment.grade = float(request.form['grade']) if request.form['grade'] else None
            db.session.commit()
            flash('Enrollment updated successfully.')
            return redirect(url_for('admin_enrollments'))
        return render_template('admin/edit_enrollment.html', enrollment=enrollment, students=students, courses=courses)

    # Delete an enrollment
    @app.route('/admin/enrollments/delete/<int:enrollment_id>', methods=['POST'])
    @login_required
    def admin_delete_enrollment(enrollment_id):
        if admin_required(): return admin_required()
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        db.session.delete(enrollment)
        db.session.commit()
        flash('Enrollment deleted successfully.')
        return redirect(url_for('admin_enrollments'))

    
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
