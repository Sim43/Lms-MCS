from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from functools import wraps
from sqlalchemy import func, or_
import os

from .app import app
from .models import db, User, Course, Category, Lesson, Enrollment
from .forms import LoginForm, StudentRegisterForm, InstructorRegisterForm, CourseForm, LessonForm

# Helper function to check if user is instructor
def instructor_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_instructor():
            flash('Access denied. Instructor access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to check if user is student
def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_student():
            flash('Access denied. Student access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp4', 'mov', 'avi'}

def allowed_file(filename, file_type='image'):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in {'png', 'jpg', 'jpeg', 'gif'}
    elif file_type == 'video':
        return ext in {'mp4', 'mov', 'avi', 'webm'}
    elif file_type == 'document':
        return ext in {'pdf', 'doc', 'docx', 'txt'}
    return ext in ALLOWED_EXTENSIONS

# Home page
@app.route('/')
def home():
    featured_courses = Course.query.filter_by(is_published=True).limit(6).all()
    categories = Category.query.limit(6).all()
    return render_template('courses/home.html', featured_courses=featured_courses, categories=categories)

# Authentication routes
@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_instructor():
            return redirect(url_for('instructor_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            if not next_page:
                if user.is_instructor():
                    next_page = url_for('instructor_dashboard')
                else:
                    next_page = url_for('student_dashboard')
            return redirect(next_page)
        flash('Invalid username or password.', 'error')
    return render_template('accounts/login.html', form=form)

@app.route('/accounts/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/accounts/register/student', methods=['GET', 'POST'])
def register_student():
    """Student registration - open to everyone"""
    if current_user.is_authenticated:
        if current_user.is_instructor():
            return redirect(url_for('instructor_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    from .forms import StudentRegisterForm
    form = StudentRegisterForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('accounts/register_student.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'error')
            return render_template('accounts/register_student.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash(f'Welcome {user.username}! Your student account has been created.', 'success')
        return redirect(url_for('student_dashboard'))
    return render_template('accounts/register_student.html', form=form)

@app.route('/accounts/register/instructor', methods=['GET', 'POST'])
def register_instructor():
    """Instructor registration - requires registration key"""
    if current_user.is_authenticated:
        if current_user.is_instructor():
            return redirect(url_for('instructor_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    from .forms import InstructorRegisterForm
    from .app import app
    
    form = InstructorRegisterForm()
    if form.validate_on_submit():
        # Verify instructor registration key
        instructor_key = app.config.get('INSTRUCTOR_REGISTRATION_KEY', 'TEACHER2024')
        if form.instructor_key.data != instructor_key:
            flash('Invalid instructor registration key. Please contact an administrator.', 'error')
            return render_template('accounts/register_instructor.html', form=form)
        
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('accounts/register_instructor.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'error')
            return render_template('accounts/register_instructor.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='instructor'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash(f'Welcome {user.username}! Your instructor account has been created.', 'success')
        return redirect(url_for('instructor_dashboard'))
    return render_template('accounts/register_instructor.html', form=form)

# Course routes
@app.route('/courses')
def course_list():
    search = request.args.get('search', '')
    category_name = request.args.get('category', '')
    
    query = Course.query.filter_by(is_published=True)
    
    if category_name:
        category = Category.query.filter_by(name=category_name).first()
        if category:
            query = query.filter_by(category_id=category.id)
    
    if search:
        query = query.filter(
            or_(
                Course.title.contains(search),
                Course.description.contains(search)
            )
        )
    
    courses = query.all()
    categories = Category.query.all()
    return render_template('courses/course_list.html', courses=courses, categories=categories, 
                         selected_category=category_name, search_query=search)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    if not course.is_published and current_user != course.instructor:
        flash('Course not found.', 'error')
        return redirect(url_for('course_list'))
    
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
        is_enrolled = enrollment is not None
    
    return render_template('courses/course_detail.html', course=course, is_enrolled=is_enrolled)

@app.route('/courses/create', methods=['GET', 'POST'])
@instructor_required
def course_create():
    form = CourseForm()
    form.category_id.choices = [(0, 'Select a category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data else None,
            is_published=True
        )
        
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename and allowed_file(file.filename, 'image'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'course_thumbnails', filename)
                file.save(filepath)
                course.thumbnail = f'course_thumbnails/{filename}'
        
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    
    return render_template('courses/course_create.html', form=form)

@app.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@instructor_required
def course_edit(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Access denied. You can only edit your own courses.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    form = CourseForm(obj=course)
    form.category_id.choices = [(0, 'Select a category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.category_id = form.category_id.data if form.category_id.data else None
        
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename and allowed_file(file.filename, 'image'):
                # Delete old thumbnail if exists
                if course.thumbnail:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], course.thumbnail)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'course_thumbnails', filename)
                file.save(filepath)
                course.thumbnail = f'course_thumbnails/{filename}'
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('courses/course_edit.html', form=form, course=course)

@app.route('/courses/<int:course_id>/delete', methods=['GET', 'POST'])
@instructor_required
def course_delete(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Access denied. You can only delete your own courses.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    if request.method == 'POST':
        # Delete thumbnail if exists
        if course.thumbnail:
            thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], course.thumbnail)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
        return redirect(url_for('instructor_dashboard'))
    
    return render_template('courses/course_delete.html', course=course)

# Lesson routes
@app.route('/lessons/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course_ref
    
    # Check if user is enrolled (for students) or is the instructor
    if current_user.is_student():
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
        if not enrollment:
            flash('You must enroll in this course to access lessons.', 'error')
            return redirect(url_for('course_detail', course_id=course.id))
    
    # Get all lessons for navigation
    lessons = lesson.course_ref.lessons
    lesson_list = list(lessons)
    current_index = lesson_list.index(lesson) if lesson in lesson_list else 0
    
    previous_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
    
    return render_template('lessons/lesson_detail.html', lesson=lesson, course=course,
                         previous_lesson=previous_lesson, next_lesson=next_lesson, lessons=lessons)

@app.route('/lessons/course/<int:course_id>/create', methods=['GET', 'POST'])
@instructor_required
def lesson_create(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Access denied. You can only add lessons to your own courses.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(
            title=form.title.data,
            course_id=course_id,
            video_url=form.video_url.data,
            text_content=form.text_content.data,
            order=form.order.data or 0
        )
        
        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and file.filename and allowed_file(file.filename, 'video'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'lesson_videos', filename)
                file.save(filepath)
                lesson.video_file = f'lesson_videos/{filename}'
        
        if 'lesson_file' in request.files:
            file = request.files['lesson_file']
            if file and file.filename and allowed_file(file.filename, 'document'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'lesson_files', filename)
                file.save(filepath)
                lesson.lesson_file = f'lesson_files/{filename}'
        
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('lesson_detail', lesson_id=lesson.id))
    
    # Get next order number
    max_order = db.session.query(func.max(Lesson.order)).filter_by(course_id=course_id).scalar() or 0
    form.order.data = max_order + 1
    
    return render_template('lessons/lesson_create.html', form=form, course=course)

@app.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@instructor_required
def lesson_edit(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course_ref
    
    if course.instructor_id != current_user.id:
        flash('Access denied. You can only edit lessons in your own courses.', 'error')
        return redirect(url_for('lesson_detail', lesson_id=lesson_id))
    
    form = LessonForm(obj=lesson)
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.video_url = form.video_url.data
        lesson.text_content = form.text_content.data
        lesson.order = form.order.data or 0
        
        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and file.filename and allowed_file(file.filename, 'video'):
                if lesson.video_file:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], lesson.video_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'lesson_videos', filename)
                file.save(filepath)
                lesson.video_file = f'lesson_videos/{filename}'
        
        if 'lesson_file' in request.files:
            file = request.files['lesson_file']
            if file and file.filename and allowed_file(file.filename, 'document'):
                if lesson.lesson_file:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], lesson.lesson_file)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'lesson_files', filename)
                file.save(filepath)
                lesson.lesson_file = f'lesson_files/{filename}'
        
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('lesson_detail', lesson_id=lesson_id))
    
    return render_template('lessons/lesson_edit.html', form=form, lesson=lesson)

@app.route('/lessons/<int:lesson_id>/delete', methods=['GET', 'POST'])
@instructor_required
def lesson_delete(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course_ref
    
    if course.instructor_id != current_user.id:
        flash('Access denied. You can only delete lessons in your own courses.', 'error')
        return redirect(url_for('lesson_detail', lesson_id=lesson_id))
    
    if request.method == 'POST':
        # Delete files if exist
        if lesson.video_file:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], lesson.video_file)
            if os.path.exists(video_path):
                os.remove(video_path)
        if lesson.lesson_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], lesson.lesson_file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    
    return render_template('lessons/lesson_delete.html', lesson=lesson)

# Enrollment routes
@app.route('/enrollments/course/<int:course_id>/enroll', methods=['GET', 'POST'])
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    
    if current_user.is_instructor():
        flash('Instructors cannot enroll in courses.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Check if already enrolled
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if enrollment:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Create enrollment
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'Successfully enrolled in {course.title}!', 'success')
    return render_template('enrollments/enrollment_success.html', course=course)

@app.route('/enrollments/course/<int:course_id>/unenroll', methods=['POST'])
@login_required
def unenroll(course_id):
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        flash('Successfully unenrolled from the course.', 'success')
    else:
        flash('You are not enrolled in this course.', 'error')
    
    return redirect(url_for('student_dashboard'))

# Dashboard routes
@app.route('/dashboard/student')
@login_required
def student_dashboard():
    if current_user.is_instructor():
        return redirect(url_for('instructor_dashboard'))
    
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_courses = [e.course_ref for e in enrollments]
    
    return render_template('dashboards/student_dashboard.html', enrolled_courses=enrolled_courses, enrollments=enrollments)

@app.route('/dashboard/instructor')
@instructor_required
def instructor_dashboard():
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    
    # Calculate statistics
    course_ids = [c.id for c in courses]
    total_enrollments = Enrollment.query.filter(Enrollment.course_id.in_(course_ids)).count()
    total_students = db.session.query(func.count(func.distinct(Enrollment.student_id))).filter(
        Enrollment.course_id.in_(course_ids)
    ).scalar() or 0
    
    return render_template('dashboards/instructor_dashboard.html', courses=courses,
                         total_enrollments=total_enrollments, total_students=total_students)

# Media file serving
@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

