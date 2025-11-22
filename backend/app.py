from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'lms-development-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['WTF_CSRF_ENABLED'] = True
# Instructor registration key - change this in production!
app.config['INSTRUCTOR_REGISTRATION_KEY'] = 'TEACHER2024'

# Initialize db from models
from .models import db
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Make csrf_token function available in templates
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=lambda: generate_csrf())

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import models after db initialization
from .models import User, Course, Category, Lesson, Enrollment

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after all initialization
from . import routes
from . import admin_routes

@app.errorhandler(404)
def page_not_found(e):
    return render_template('courses/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('courses/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create upload directories
        media_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(media_folder, 'profile_pictures'), exist_ok=True)
        os.makedirs(os.path.join(media_folder, 'course_thumbnails'), exist_ok=True)
        os.makedirs(os.path.join(media_folder, 'lesson_videos'), exist_ok=True)
        os.makedirs(os.path.join(media_folder, 'lesson_files'), exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

