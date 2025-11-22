#!/bin/bash

# LMS Setup Script for Flask

echo "========================================="
echo "Learning Management System - Setup"
echo "========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"

# Create media directories
echo ""
echo "📁 Creating media directories..."
mkdir -p media/profile_pictures media/course_thumbnails media/lesson_videos media/lesson_files
echo "✅ Media directories created"

# Create database (will be created on first run)
echo ""
echo "🗄️  Database will be created on first run"

# Setup complete
echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the Flask application:"
echo "   python run.py"
echo "   OR"
echo "   cd backend && python app.py"
echo ""
echo "3. Access the application at:"
echo "   http://localhost:5000"
echo ""
echo "4. Create an admin user:"
echo "   python create_admin.py"
echo "   OR"
echo "   python create_admin.py --username admin --email admin@example.com --password admin123 --non-interactive"
echo ""
echo "5. Access admin panel at:"
echo "   http://localhost:5000/admin"
echo ""
echo "6. Registration:"
echo "   - Students: http://localhost:5000/accounts/register/student"
echo "   - Instructors: http://localhost:5000/accounts/register/instructor"
echo "     (Default registration key: TEACHER2024)"
echo ""
echo "========================================="
echo ""

