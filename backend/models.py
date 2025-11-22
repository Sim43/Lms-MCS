from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import string

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'instructor', or 'admin'
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='instructor_ref', lazy=True, foreign_keys='Course.instructor_id')
    enrollments = db.relationship('Enrollment', backref='student_ref', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_instructor(self):
        return self.role == 'instructor'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_role_display(self):
        role_map = {
            'admin': 'Administrator',
            'instructor': 'Instructor',
            'student': 'Student'
        }
        return role_map.get(self.role, 'Student')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='category_ref', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    course_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course_ref', lazy=True, order_by='Lesson.order')
    enrollments = db.relationship('Enrollment', backref='course_ref', lazy=True)
    
    @property
    def instructor(self):
        return User.query.get(self.instructor_id)
    
    @property
    def category(self):
        return Category.query.get(self.category_id) if self.category_id else None
    
    def get_enrollment_count(self):
        return len(self.enrollments)
    
    def get_lessons_count(self):
        return len(self.lessons)
    
    @staticmethod
    def generate_course_code():
        """Generate a unique 8-character alphanumeric course code"""
        while True:
            # Generate 8-character code (uppercase letters and numbers)
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Check if code already exists
            if not Course.query.filter_by(course_code=code).first():
                return code
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    video_url = db.Column(db.String(500), nullable=True)
    video_file = db.Column(db.String(255), nullable=True)
    text_content = db.Column(db.Text, nullable=True)
    lesson_file = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def course(self):
        return Course.query.get(self.course_id)
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)
    
    @property
    def student(self):
        return User.query.get(self.student_id)
    
    @property
    def course(self):
        return Course.query.get(self.course_id)
    
    def __repr__(self):
        return f'<Enrollment {self.student_id} - {self.course_id}>'

