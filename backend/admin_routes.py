from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
from sqlalchemy import or_
import os

from .app import app
from .models import db, User, Course, Category, Lesson, Enrollment

# Admin decorator - only admins can access
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access denied. Admin access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Bootstrap-based admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'total_courses': Course.query.count(),
        'total_lessons': Lesson.query.count(),
        'total_enrollments': Enrollment.query.count(),
        'total_categories': Category.query.count(),
        'total_instructors': User.query.filter_by(role='instructor').count(),
        'total_students': User.query.filter_by(role='student').count(),
        'published_courses': Course.query.filter_by(is_published=True).count(),
        'unpublished_courses': Course.query.filter_by(is_published=False).count(),
    }
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users, recent_courses=recent_courses)

@app.route('/admin/users')
@admin_required
def admin_users():
    """Manage users"""
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, search=search, role_filter=role_filter)

@app.route('/admin/users/<int:user_id>/toggle')
@admin_required
def admin_toggle_user(user_id):
    """Toggle user active status or role"""
    user = User.query.get_or_404(user_id)
    action = request.args.get('action', '')
    
    # Prevent admin from changing their own role
    if user.id == current_user.id and action != 'delete':
        flash('You cannot change your own role.', 'error')
        return redirect(url_for('admin_users'))
    
    if action == 'delete':
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin_users'))
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    elif action == 'make_instructor':
        user.role = 'instructor'
        db.session.commit()
        flash(f'{user.username} is now an instructor.', 'success')
    elif action == 'make_student':
        user.role = 'student'
        db.session.commit()
        flash(f'{user.username} is now a student.', 'success')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/courses')
@admin_required
def admin_courses():
    """Manage courses"""
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = Course.query
    
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'unpublished':
        query = query.filter_by(is_published=False)
    
    if search:
        query = query.filter(
            or_(
                Course.title.contains(search),
                Course.description.contains(search)
            )
        )
    
    courses = query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses, search=search, status=status)

@app.route('/admin/courses/<int:course_id>/toggle')
@admin_required
def admin_toggle_course(course_id):
    """Toggle course published status"""
    course = Course.query.get_or_404(course_id)
    action = request.args.get('action', '')
    
    if action == 'publish':
        course.is_published = True
        db.session.commit()
        flash('Course published successfully.', 'success')
    elif action == 'unpublish':
        course.is_published = False
        db.session.commit()
        flash('Course unpublished successfully.', 'success')
    elif action == 'delete':
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully.', 'success')
    
    return redirect(url_for('admin_courses'))

@app.route('/admin/categories')
@admin_required
def admin_categories():
    """Manage categories"""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/create', methods=['POST'])
@admin_required
def admin_create_category():
    """Create category"""
    name = request.form.get('name', '').strip()
    
    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('admin_categories'))
    
    if Category.query.filter_by(name=name).first():
        flash('Category already exists.', 'error')
        return redirect(url_for('admin_categories'))
    
    category = Category(name=name, description=request.form.get('description', ''))
    db.session.add(category)
    db.session.commit()
    
    flash('Category created successfully.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    """Delete category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category is used by any courses
    if category.courses:
        flash('Cannot delete category. It is being used by courses.', 'error')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/lessons')
@admin_required
def admin_lessons():
    """Manage lessons"""
    course_id = request.args.get('course_id', type=int)
    
    if course_id:
        lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
        course = Course.query.get_or_404(course_id)
        return render_template('admin/lessons.html', lessons=lessons, course=course)
    
    lessons = Lesson.query.order_by(Lesson.created_at.desc()).limit(50).all()
    return render_template('admin/lessons.html', lessons=lessons, course=None)

@app.route('/admin/enrollments')
@admin_required
def admin_enrollments():
    """View enrollments"""
    course_id = request.args.get('course_id', type=int)
    
    if course_id:
        enrollments = Enrollment.query.filter_by(course_id=course_id).order_by(Enrollment.enrolled_at.desc()).all()
        course = Course.query.get_or_404(course_id)
        return render_template('admin/enrollments.html', enrollments=enrollments, course=course)
    
    enrollments = Enrollment.query.order_by(Enrollment.enrolled_at.desc()).limit(100).all()
    return render_template('admin/enrollments.html', enrollments=enrollments, course=None)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Admin settings page"""
    from .app import app
    instructor_key = app.config.get('INSTRUCTOR_REGISTRATION_KEY', 'TEACHER2024')
    return render_template('admin/settings.html', instructor_key=instructor_key)

@app.route('/admin/users/<int:user_id>/make_admin', methods=['POST'])
@admin_required
def admin_make_admin(user_id):
    """Make a user an admin"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'error')
        return redirect(url_for('admin_users'))
    
    user.role = 'admin'
    db.session.commit()
    flash(f'{user.username} is now an administrator.', 'success')
    return redirect(url_for('admin_users'))

