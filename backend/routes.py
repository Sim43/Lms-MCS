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
        if current_user.is_admin():
            flash('Access denied. Admin users cannot access instructor features.', 'error')
            return redirect(url_for('admin_dashboard'))
        if not current_user.is_instructor():
            flash('Access denied. Instructor access required.', 'error')
            if current_user.is_student():
                return redirect(url_for('student_dashboard'))
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
    """Home page - courses are now private, enrollment by code only"""
    # Redirect admins to admin panel immediately
    if current_user.is_authenticated and current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    
    categories = Category.query.limit(6).all()
    return render_template('courses/home.html', categories=categories)

# Authentication routes
@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        elif current_user.is_instructor():
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
                if user.is_admin():
                    next_page = url_for('admin_dashboard')
                elif user.is_instructor():
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
    """Course listing - only shows courses the user is enrolled in or is an instructor"""
    # Admins should use admin panel
    if current_user.is_authenticated and current_user.is_admin():
        flash('Please use the Admin Panel to manage courses.', 'info')
        return redirect(url_for('admin_courses'))
    
    search = request.args.get('search', '')
    # Support multiple category selection
    category_names = request.args.getlist('category')  # Get list of selected categories
    
    # For non-authenticated users, show empty list
    if not current_user.is_authenticated:
        courses = []
    elif current_user.is_instructor():
        # Instructors can see their own courses
        query = Course.query.filter_by(instructor_id=current_user.id, is_published=True)
        if category_names:
            # Filter by multiple categories
            category_objs = Category.query.filter(Category.name.in_(category_names)).all()
            if category_objs:
                category_ids = [c.id for c in category_objs]
                query = query.filter(Course.category_id.in_(category_ids))
        if search:
            query = query.filter(
                or_(
                    Course.title.contains(search),
                    Course.description.contains(search)
                )
            )
        courses = query.all()
    else:
        # Students can only see courses they're enrolled in
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        enrolled_course_ids = [e.course_id for e in enrollments]
        if not enrolled_course_ids:
            courses = []
        else:
            query = Course.query.filter(Course.id.in_(enrolled_course_ids), Course.is_published == True)
            if category_names:
                # Filter by multiple categories
                category_objs = Category.query.filter(Category.name.in_(category_names)).all()
                if category_objs:
                    category_ids = [c.id for c in category_objs]
                    query = query.filter(Course.category_id.in_(category_ids))
            if search:
                query = query.filter(
                    or_(
                        Course.title.contains(search),
                        Course.description.contains(search)
                    )
                )
            courses = query.all()  # Always execute query
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('courses/course_list.html', courses=courses, categories=categories, 
                         selected_categories=category_names, search_query=search)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check access permissions
    can_access = False
    is_enrolled = False
    
    if not current_user.is_authenticated:
        flash('Please login to view course details.', 'error')
        return redirect(url_for('login'))
    
    # Admins should use admin panel, redirect them
    if current_user.is_admin():
        flash('Please use the Admin Panel to manage courses.', 'info')
        return redirect(url_for('admin_courses'))
    # Instructors can access their own courses
    elif current_user.is_instructor() and course.instructor_id == current_user.id:
        can_access = True
    # Students can access courses they're enrolled in
    elif current_user.is_student():
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
        if enrollment:
            is_enrolled = True
            can_access = True
    
    if not can_access:
        flash('You must enroll in this course using the course code to access it.', 'error')
        return redirect(url_for('enroll_by_code'))
    
    if current_user.is_student() and not is_enrolled:
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
        is_enrolled = enrollment is not None
    
    return render_template('courses/course_detail.html', course=course, is_enrolled=is_enrolled)

@app.route('/courses/create', methods=['GET', 'POST'])
@instructor_required
def course_create():
    from .category_codes import get_category_code_choices, normalize_category_code
    
    # Get choices first
    category_choices = get_category_code_choices()
    
    # Create form - choices will be set in __init__ method
    form = CourseForm()
    # Ensure choices are set (in case __init__ didn't work)
    if not form.category_code.choices or len(form.category_code.choices) <= 1:
        form.category_code.choices = category_choices
    
    if form.validate_on_submit():
        # Ensure choices are still set during validation
        form.category_code.choices = category_choices
        # Handle category code
        category_id = None
        category_code_value = form.category_code.data
        
        if category_code_value == 'OTHER':
            # Use custom category code from "Other" field
            custom_code = normalize_category_code(form.category_other.data)
            if custom_code:
                # Find or create category with this code
                category = Category.query.filter_by(name=custom_code).first()
                if not category:
                    category = Category(name=custom_code, description=f'Custom category: {custom_code}')
                    db.session.add(category)
                    db.session.commit()
                category_id = category.id
        elif category_code_value and category_code_value != '' and category_code_value != 'OTHER':
            # Use predefined category code (the value is already just the code like "CS", "EE", etc.)
            code = normalize_category_code(category_code_value)
            if code:
                # Find or create category with this code
                category = Category.query.filter_by(name=code).first()
                if not category:
                    category = Category(name=code, description=f'Category: {code}')
                    db.session.add(category)
                    db.session.commit()
                category_id = category.id
        
        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor_id=current_user.id,
            category_id=category_id,
            is_published=True,
            course_code=Course.generate_course_code()
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
    
    # Ensure choices are set again after validation (in case validation fails)
    form.category_code.choices = get_category_code_choices()
    
    return render_template('courses/course_create.html', form=form)

@app.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@instructor_required
def course_edit(course_id):
    from .category_codes import get_category_code_choices, normalize_category_code
    
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Access denied. You can only edit your own courses.', 'error')
        return redirect(url_for('course_detail', course_id=course_id))
    
    form = CourseForm(obj=course)
    # Set category code choices
    form.category_code.choices = get_category_code_choices()
    
    # Set current category code if exists
    if course.category:
        current_category_name = course.category.name
        # Try to match with predefined codes
        choices_list = get_category_code_choices()
        choices_dict = {code: display for code, display in choices_list}
        
        # Check if current category matches any predefined code
        if current_category_name in choices_dict:
            form.category_code.data = current_category_name
        else:
            # It's a custom category, set to "OTHER" and fill the other field
            form.category_code.data = 'OTHER'
            form.category_other.data = current_category_name
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        
        # Handle category code
        category_id = None
        category_code_value = form.category_code.data
        
        if category_code_value == 'OTHER':
            # Use custom category code from "Other" field
            custom_code = normalize_category_code(form.category_other.data)
            if custom_code:
                # Find or create category with this code
                category = Category.query.filter_by(name=custom_code).first()
                if not category:
                    category = Category(name=custom_code, description=f'Custom category: {custom_code}')
                    db.session.add(category)
                    db.session.commit()
                category_id = category.id
        elif category_code_value and category_code_value != '':
            # Use predefined category code
            code = category_code_value.split(' - ')[0] if ' - ' in category_code_value else category_code_value
            code = normalize_category_code(code)
            if code:
                # Find or create category with this code
                category = Category.query.filter_by(name=code).first()
                if not category:
                    category = Category(name=code, description=f'Category: {code}')
                    db.session.add(category)
                    db.session.commit()
                category_id = category.id
        
        course.category_id = category_id
        
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
    
    # Ensure choices are set again after validation
    form.category_code.choices = get_category_code_choices()
    if course.category:
        current_category_name = course.category.name
        choices_list = get_category_code_choices()
        choices_dict = {code: display for code, display in choices_list}
        
        # Check if current category matches any predefined code
        if current_category_name in choices_dict:
            form.category_code.data = current_category_name
        else:
            form.category_code.data = 'OTHER'
            form.category_other.data = current_category_name
    
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
@app.route('/enroll', methods=['GET', 'POST'])
@login_required
def enroll_by_code():
    """Enroll in a course using course code"""
    if current_user.is_admin():
        flash('Admin users cannot enroll in courses. Please use the Admin Panel.', 'error')
        return redirect(url_for('admin_dashboard'))
    if current_user.is_instructor():
        flash('Instructors cannot enroll in courses.', 'error')
        return redirect(url_for('instructor_dashboard'))
    
    from .forms import EnrollmentForm
    form = EnrollmentForm()
    
    if form.validate_on_submit():
        course_code = form.course_code.data.upper().strip()
        course = Course.query.filter_by(course_code=course_code).first()
        
        if not course:
            flash('Invalid course code. Please check and try again.', 'error')
            return render_template('enrollments/enroll.html', form=form)
        
        if not course.is_published:
            flash('This course is not available for enrollment.', 'error')
            return render_template('enrollments/enroll.html', form=form)
        
        # Check if already enrolled
        enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
        if enrollment:
            flash(f'You are already enrolled in "{course.title}".', 'info')
            return redirect(url_for('course_detail', course_id=course.id))
        
        # Create enrollment
        enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
        db.session.add(enrollment)
        db.session.commit()
        
        flash(f'Successfully enrolled in {course.title}!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    
    return render_template('enrollments/enroll.html', form=form)

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
    # Only students can access student dashboard
    if current_user.is_admin():
        flash('Access denied. Admin users cannot access student dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))
    if current_user.is_instructor():
        flash('Access denied. Instructors cannot access student dashboard.', 'error')
        return redirect(url_for('instructor_dashboard'))
    
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    enrolled_courses = [e.course_ref for e in enrollments]
    
    return render_template('dashboards/student_dashboard.html', enrolled_courses=enrolled_courses, enrollments=enrollments)

@app.route('/dashboard/instructor')
@instructor_required
def instructor_dashboard():
    # Only instructors can access instructor dashboard
    if current_user.is_admin():
        flash('Access denied. Admin users cannot access instructor dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))
    
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

