# Learning Management System (LMS)

A complete full-stack Learning Management System built with Django, featuring student and instructor roles, course management, lesson delivery, and enrollment system.

## Features

### Authentication
- Student and Instructor account registration
- Login/logout functionality
- Role-based access control
- Profile management

### Course Management
- List all available courses
- Course detail pages with description, instructor, and thumbnail
- Category-based organization
- Search functionality
- Instructors can create, edit, and delete courses

### Lesson Management
- Lesson title and content
- Support for video URLs (YouTube) and video file uploads
- Text content for lessons
- File attachments (PDF, DOCX, etc.)
- Lesson ordering within courses

### Enrollment System
- Free enrollment for students
- "Enroll Now" button on course pages
- Enrollment stored in database
- Students can only access lessons for enrolled courses

### Dashboards
- **Student Dashboard**: View enrolled courses, continue learning
- **Instructor Dashboard**: Manage courses and lessons, view statistics

### Pages
- Home page with featured courses
- Courses listing page
- Course detail pages
- Enrollment success page
- Student and Instructor dashboards
- Custom 404 and 500 error pages

### Admin Panel
- Django admin interface to manage all data
- User management
- Course and lesson management
- Enrollment tracking

## Technology Stack

- **Backend**: Python 3, Django 4.2
- **Database**: SQLite (default, can be switched to PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Media**: Local storage for images and files (can be configured for AWS S3)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Navigate to Project

```bash
cd /home/zero/Downloads/lms_website
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (for Admin Panel)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Create Media Directory

```bash
mkdir -p media/profile_pictures media/course_thumbnails media/lesson_videos media/lesson_files
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
lms_website/
├── accounts/          # User authentication app
├── courses/           # Course management app
├── lessons/           # Lesson management app
├── enrollments/       # Enrollment system app
├── dashboards/        # Dashboard views app
├── lms_project/       # Main Django project settings
├── templates/         # HTML templates
├── media/             # User uploaded files
├── static/            # Static files (CSS, JS, images)
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Usage Guide

### For Students

1. **Register/Login**: Create a student account or login
2. **Browse Courses**: Explore available courses on the courses page
3. **Enroll**: Click "Enroll Now" on any course (free enrollment)
4. **Learn**: Access lessons from your dashboard or course page
5. **Dashboard**: View all your enrolled courses

### For Instructors

1. **Register/Login**: Create an instructor account or login
2. **Create Course**: Click "Create New Course" from dashboard
3. **Add Lessons**: Click "Add Lesson" from course detail page
4. **Manage**: Edit or delete courses and lessons as needed
5. **View Stats**: See enrollments and student count in dashboard

## Admin Panel

Access the admin panel at `http://127.0.0.1:8000/admin/`

Use your superuser credentials to:
- Manage users, courses, lessons, and enrollments
- Create categories
- View system-wide statistics

## Configuration

### Database

To switch to PostgreSQL, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Media Storage

For production, configure AWS S3 or another cloud storage service in `settings.py`.

## Development Notes

- All enrollment is free (no payment integration)
- Students can only access lessons for courses they're enrolled in
- Instructors can manage their own courses only
- Video URLs support YouTube (auto-converted to embed format)
- Supports video file uploads and various file types

## Troubleshooting

### Migration Errors
If you encounter migration errors:
```bash
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Media Files Not Showing
Ensure the `media/` directory exists and has proper permissions:
```bash
chmod 755 media/
```

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to fork, modify, and improve this LMS system!

