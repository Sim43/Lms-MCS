# Learning Management System (LMS)

A complete full-stack Learning Management System built with **Flask** (Python backend) and **Bootstrap 5** (HTML/CSS/JavaScript frontend). Features student and instructor roles, course management, lesson delivery, and a free enrollment system.

## 🚀 Features

### Authentication
- ✅ User registration with Student/Instructor roles
- ✅ Login/logout functionality
- ✅ Role-based access control
- ✅ Session management

### Course Management
- ✅ Create, edit, and delete courses (Instructors)
- ✅ Course listing with search and category filters
- ✅ Course detail pages with descriptions and thumbnails
- ✅ Category-based organization

### Lesson Management
- ✅ Create, edit, and delete lessons (Instructors)
- ✅ Support for YouTube video URLs (auto-embed)
- ✅ Video file uploads
- ✅ Text content
- ✅ File attachments (PDF, DOCX, etc.)
- ✅ Lesson ordering within courses

### Enrollment System
- ✅ Free enrollment for students
- ✅ "Enroll Now" button on course pages
- ✅ Enrollment tracking
- ✅ Access control (only enrolled students can view lessons)

### Dashboards
- ✅ **Student Dashboard**: View enrolled courses, continue learning
- ✅ **Instructor Dashboard**: Manage courses, view statistics
- ✅ **Admin Dashboard**: Bootstrap-based admin panel for system management

### Admin Panel
- ✅ Bootstrap 5 based admin interface
- ✅ User management
- ✅ Course management
- ✅ Category management
- ✅ Lesson management
- ✅ Enrollment tracking
- ✅ Statistics dashboard

## 📁 Project Structure

```
lms_website/
├── backend/                    # Flask backend application
│   ├── __init__.py            # Package initialization
│   ├── app.py                 # Main Flask application (config, db, login manager)
│   ├── models.py              # SQLAlchemy database models (User, Course, Category, Lesson, Enrollment)
│   ├── routes.py              # Main application routes (auth, courses, lessons, dashboards)
│   ├── admin_routes.py        # Admin panel routes (user/course/category management)
│   └── forms.py               # WTForms form definitions (Login, Register, Course, Lesson)
│
├── frontend/                   # Frontend assets
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html          # Base template with navigation
│   │   ├── accounts/          # Authentication templates
│   │   │   ├── login.html
│   │   │   ├── register_student.html
│   │   │   └── register_instructor.html
│   │   ├── courses/           # Course templates
│   │   │   ├── home.html
│   │   │   ├── course_list.html
│   │   │   ├── course_detail.html
│   │   │   ├── course_create.html
│   │   │   ├── course_edit.html
│   │   │   ├── course_delete.html
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   ├── lessons/           # Lesson templates
│   │   │   ├── lesson_detail.html
│   │   │   ├── lesson_create.html
│   │   │   ├── lesson_edit.html
│   │   │   └── lesson_delete.html
│   │   ├── dashboards/        # Dashboard templates
│   │   │   ├── student_dashboard.html
│   │   │   └── instructor_dashboard.html
│   │   ├── enrollments/       # Enrollment templates
│   │   │   └── enrollment_success.html
│   │   └── admin/             # Admin panel templates
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── users.html
│   │       ├── courses.html
│   │       ├── categories.html
│   │       ├── lessons.html
│   │       ├── enrollments.html
│   │       └── settings.html
│   └── static/                # Static files (CSS, JS, images)
│       └── favicon.png        # Favicon
│
├── media/                      # User-uploaded files (auto-created, gitignored)
│   ├── profile_pictures/
│   ├── course_thumbnails/
│   ├── lesson_videos/
│   └── lesson_files/
│
├── venv/                       # Virtual environment (not in repo, gitignored)
│
├── run.py                      # Application entry point
├── create_admin.py             # Script to create admin users
├── setup.sh                    # Setup script for easy installation
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

### Backend Structure

- **`backend/app.py`** - Main Flask application initialization, configuration, database and login manager setup, error handlers
- **`backend/models.py`** - SQLAlchemy database models (User, Course, Category, Lesson, Enrollment)
- **`backend/routes.py`** - Main application routes (authentication, courses, lessons, enrollments, dashboards, media serving)
- **`backend/admin_routes.py`** - Admin panel routes (user/course/category/lesson/enrollment management)
- **`backend/forms.py`** - WTForms form definitions (LoginForm, StudentRegisterForm, InstructorRegisterForm, CourseForm, LessonForm)

### Frontend Structure

- **Templates** - Jinja2 templates with Bootstrap 5 styling
  - Base template with navigation
  - Authentication pages (login, student/instructor registration)
  - Course pages (listing, detail, create, edit, delete)
  - Lesson pages (viewing, creating, editing)
  - Dashboard pages (student, instructor)
  - Admin panel (fully Bootstrap-based)
- **Static Files** - CSS/JS via Bootstrap CDN, custom favicon

### File Organization Principles

- **Backend code** → `backend/` folder
- **Frontend templates** → `frontend/templates/`
- **Static assets** → `frontend/static/`
- **Uploaded files** → `media/` folder (gitignored)
- **Configuration** → Root level (requirements.txt, setup.sh)
- **Documentation** → Root level (README.md)

## 🛠️ Technology Stack

### Backend
- **Flask** 3.0.0 - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling
- **Werkzeug** - Security utilities

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling
- **JavaScript** - Interactivity
- **Bootstrap 5** - Responsive UI framework
- **Bootstrap Icons** - Icon library

### Database
- **SQLite** - Default database (can be configured for PostgreSQL)

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

**Option 1: Using setup script**
```bash
chmod +x setup.sh
./setup.sh
```

**Option 2: Manual setup**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create media directories
mkdir -p media/profile_pictures media/course_thumbnails media/lesson_videos media/lesson_files

# Run the application
cd backend
python app.py
```

The application will be available at `http://localhost:5000`

### Create Admin User

After running the app, create an admin user using the provided script:

```bash
# Interactive mode (recommended)
python create_admin.py

# Non-interactive mode
python create_admin.py --username admin --email admin@example.com --password admin123 --non-interactive
```

**Or** create manually using Python:

```python
python
>>> from backend.app import app
>>> from backend.models import db, User
>>> with app.app_context():
...     admin = User(username='admin', email='admin@example.com', role='admin')
...     admin.set_password('admin123')
...     db.session.add(admin)
...     db.session.commit()
...     print('Admin user created!')
```

## 🎯 Usage Guide

### For Students

1. **Register**: Create a student account
2. **Browse Courses**: Explore available courses
3. **Enroll**: Click "Enroll Now" on any course (free!)
4. **Learn**: Access lessons from your dashboard
5. **Dashboard**: View all enrolled courses

### For Instructors

1. **Register**: Create an instructor account
2. **Create Course**: Click "Create New Course" from dashboard
3. **Add Lessons**: Click "Add Lesson" from course detail page
4. **Manage**: Edit or delete courses and lessons
5. **Statistics**: View enrollments and student count

### For Admins

**Admin Capabilities:**
- ✅ **Full System Access**: Manage all users, courses, lessons, categories, and enrollments
- ✅ **User Management**: 
  - View all users (students, instructors, admins)
  - Change user roles (make student → instructor, etc.)
  - Delete users
  - Create admin users
- ✅ **Course Management**: 
  - View all courses (published and unpublished)
  - Publish/unpublish courses
  - Delete any course
- ✅ **Category Management**: 
  - Create, edit, and delete categories
- ✅ **Lesson Management**: 
  - View all lessons across all courses
- ✅ **Enrollment Management**: 
  - View all enrollments
  - Filter by course
- ✅ **Statistics Dashboard**: 
  - Total users, courses, lessons, enrollments
  - Published vs unpublished courses
  - Recent activity
- ✅ **Settings**: 
  - View/configure instructor registration key
  - System configuration

**How to Use:**
1. **Login**: Use admin credentials
2. **Access Admin Panel**: Click "Admin Panel" in dropdown menu or go to `/admin`
3. **Navigate**: Use the admin navigation to manage different sections
4. **Manage Resources**: Edit, delete, or modify any resource in the system

## 🔑 Key Routes

- `/` - Home page
- `/courses` - Course listing
- `/courses/<id>` - Course detail
- `/accounts/login` - Login page
- `/accounts/register/student` - Student registration (open to everyone)
- `/accounts/register/instructor` - Instructor registration (requires registration key)
- `/dashboard/student` - Student dashboard
- `/dashboard/instructor` - Instructor dashboard
- `/admin` - Admin dashboard
- `/admin/users` - User management
- `/admin/courses` - Course management
- `/admin/categories` - Category management
- `/admin/lessons` - Lesson management
- `/admin/enrollments` - Enrollment management
- `/admin/settings` - Admin settings (instructor registration key)

## 📝 Development Notes

### Registration System

**Student Registration:**
- Open to everyone - no special requirements
- Navigate to `/accounts/register/student`
- Students can enroll in courses and learn

**Instructor Registration:**
- Requires a special registration key
- Navigate to `/accounts/register/instructor`
- Default key: `TEACHER2024` (configurable in `backend/app.py`)
- Instructors can create and manage courses

**Admin Access:**
- Admin users must be created by existing admins or via the `create_admin.py` script
- Admins have full system access

### Security Features

- **Role-Based Access Control**: Students, Instructors, and Admins have different permissions
- **Instructor Registration Key**: Prevents unauthorized instructor account creation
- **CSRF Protection**: All forms are protected against CSRF attacks
- **Password Hashing**: Passwords are securely hashed using Werkzeug

### Features

- All enrollment is free (no payment integration)
- Students can only access lessons for courses they're enrolled in
- Instructors can manage their own courses only
- Admins can manage everything
- Video URLs support YouTube (auto-converted to embed format)
- Supports video file uploads and various file types
- Admin panel is fully Bootstrap-based

## 🔧 Configuration

### Database

To switch to PostgreSQL, update `backend/app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/lms_db'
```

### Media Storage

Media files are stored locally by default. For production, configure AWS S3 or another cloud storage service.

## 🚀 Deployment

### Deploying to GitHub

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   ```

2. **Add All Files**:
   ```bash
   git add .
   ```

3. **Create Initial Commit**:
   ```bash
   git commit -m "Initial commit: Flask LMS system"
   ```

4. **Create GitHub Repository**:
   - Go to [GitHub](https://github.com) and create a new repository
   - Do NOT initialize with README, .gitignore, or license (we already have them)

5. **Add Remote and Push**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

6. **Verify Upload**:
   - Check that all files are uploaded (except those in `.gitignore`)
   - Verify `venv/`, `media/`, `*.db`, and `__pycache__/` are NOT uploaded

### Production Deployment Checklist

- [ ] Change `SECRET_KEY` in `backend/app.py` to a secure random string
- [ ] Set `DEBUG = False` in production
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up cloud storage for media files (AWS S3, etc.)
- [ ] Configure environment variables for sensitive data
- [ ] Set up proper logging
- [ ] Configure HTTPS with SSL certificate
- [ ] Set up automated backups
- [ ] Configure firewall and security settings
- [ ] Use production WSGI server (Gunicorn, uWSGI)

### Popular Deployment Platforms

**Heroku:**
```bash
# Install Heroku CLI
heroku create your-app-name
git push heroku main
```

**PythonAnywhere:**
- Upload files via web interface or Git
- Configure WSGI file
- Set up virtual environment

**DigitalOcean / AWS / Azure:**
- Use Docker or traditional server setup
- Install dependencies and configure reverse proxy (Nginx)
- Use Gunicorn as WSGI server

**Vercel / Netlify:**
- Configure build settings
- Set up environment variables
- Deploy via Git integration

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and improve this LMS system!

## 📧 Support

For issues or questions, please open an issue on the repository.

---

**Built with ❤️ using Flask and Bootstrap 5**
