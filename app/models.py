from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, or admin
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# In models.py
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    meeting_time = db.Column(db.String(120), nullable=True)  # New column for meeting times
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to the teacher
    teacher = db.relationship('User', backref='courses')  # Relationship to the teacher
    enrollments = db.relationship('Enrollment', back_populates='course', lazy='dynamic')

    def __repr__(self):
        return f'<Course {self.name}>'



class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.Float)
    # Use back_populates to define a two-way relationship without conflicting backrefs
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment student_id={self.student_id}, course_id={self.course_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
