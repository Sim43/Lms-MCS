#!/bin/bash

# LMS Setup Script

echo "Setting up Learning Management System..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create media directories
echo "Creating media directories..."
mkdir -p media/profile_pictures media/course_thumbnails media/lesson_videos media/lesson_files
mkdir -p static staticfiles

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create a superuser account:"
echo "   python manage.py createsuperuser"
echo ""
echo "2. Run the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Access the application at:"
echo "   http://127.0.0.1:8000/"
echo ""
echo "4. Access the admin panel at:"
echo "   http://127.0.0.1:8000/admin/"
echo ""

