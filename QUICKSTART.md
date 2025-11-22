# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Run Setup Script (Optional)
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Or Manual Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Access URLs

- **Home**: http://127.0.0.1:8000/
- **Courses**: http://127.0.0.1:8000/courses/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Register**: http://127.0.0.1:8000/accounts/register/

## Quick Test Flow

1. **Register as Instructor**
   - Go to Register page
   - Select "Instructor" role
   - Create account

2. **Create a Course**
   - Login with instructor account
   - Go to Dashboard
   - Click "Create New Course"
   - Fill in details and save

3. **Add Lessons**
   - Go to Course Detail page
   - Click "Add Lesson"
   - Add video URL (YouTube) or upload file
   - Add text content

4. **Register as Student**
   - Logout
   - Register new account as "Student"
   - Browse courses

5. **Enroll in Course**
   - View course details
   - Click "Enroll Now" (free!)
   - Access lessons

## Features Summary

✅ **Authentication**: Student/Instructor roles
✅ **Courses**: Create, edit, delete, list, search
✅ **Lessons**: Video URLs, file uploads, text content
✅ **Enrollment**: Free enrollment system
✅ **Dashboards**: Student and Instructor views
✅ **Admin Panel**: Full Django admin
✅ **UI**: Bootstrap 5 responsive design

## Next Steps

- Add more courses and lessons
- Customize templates
- Configure database (PostgreSQL for production)
- Set up media storage (AWS S3 for production)
- Add more features as needed!

