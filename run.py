#!/usr/bin/env python3
"""
Run script for LMS Flask application
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app

if __name__ == '__main__':
    with app.app_context():
        from backend.models import db
        db.create_all()
        
        # Create upload directories
        media_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(media_folder, 'profile_pictures'), exist_ok=True)
        os.makedirs(os.path.join(media_folder, 'course_thumbnails'), exist_ok=True)
        os.makedirs(os.path.join(media_folder, 'lesson_videos'), exist_ok=True)
        os.makedirs(os.path.join(media_folder, 'lesson_files'), exist_ok=True)
    
    print("=" * 50)
    print("Learning Management System")
    print("=" * 50)
    print("Server starting on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

