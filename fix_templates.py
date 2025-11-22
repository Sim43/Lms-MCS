#!/usr/bin/env python3
"""
Script to convert Django template syntax to Flask/Jinja2 syntax
"""
import os
import re
from pathlib import Path

TEMPLATE_DIR = Path('frontend/templates')

# Common Django to Flask conversions
CONVERSIONS = [
    # Remove {% load static %}
    (r'{%\s*load\s+static\s*%}', ''),
    
    # {% url 'name' %} -> {{ url_for('name') }}
    (r"{%\s*url\s+'([^']+)'\s*%}", r"{{ url_for('\1') }}"),
    
    # {% url 'name' pk %} -> {{ url_for('name', id=pk) }}
    (r"{%\s*url\s+'([^']+):([^']+)'\s+(\w+)\.pk\s*%}", r"{{ url_for('\2', course_id=\3.id) }}"),
    (r"{%\s*url\s+'([^']+):([^']+)'\s+(\w+)\.id\s*%}", r"{{ url_for('\2', course_id=\3.id) }}"),
    (r"{%\s*url\s+'([^']+):([^']+)'\s+(\w+)\.(\w+)\s*%}", r"{{ url_for('\2', \1_id=\3.\4) }}"),
    
    # Specific URL patterns
    (r"{%\s*url\s+'courses:home'\s*%}", r"{{ url_for('home') }}"),
    (r"{%\s*url\s+'courses:course_list'\s*%}", r"{{ url_for('course_list') }}"),
    (r"{%\s*url\s+'accounts:login'\s*%}", r"{{ url_for('login') }}"),
    (r"{%\s*url\s+'accounts:register'\s*%}", r"{{ url_for('register') }}"),
    (r"{%\s*url\s+'accounts:logout'\s*%}", r"{{ url_for('logout') }}"),
    (r"{%\s*url\s+'dashboards:student_dashboard'\s*%}", r"{{ url_for('student_dashboard') }}"),
    (r"{%\s*url\s+'dashboards:instructor_dashboard'\s*%}", r"{{ url_for('instructor_dashboard') }}"),
    
    # user -> current_user
    (r'\buser\.is_authenticated\b', 'current_user.is_authenticated'),
    (r'\buser\.is_instructor\b', 'current_user.is_instructor()'),
    (r'\buser\.is_student\b', 'current_user.is_student()'),
    (r'\buser\.username\b', 'current_user.username'),
    (r'\buser\.get_role_display\b', 'current_user.get_role_display()'),
    (r'\buser\b(?!\.)', 'current_user'),
    
    # .pk -> .id
    (r'\.pk\b', '.id'),
    
    # .url for media files
    (r'(\w+)\.thumbnail\.url', r"url_for('media', filename=\1.thumbnail) if \1.thumbnail else ''"),
    (r'(\w+)\.video_file\.url', r"url_for('media', filename=\1.video_file) if \1.video_file else ''"),
    (r'(\w+)\.lesson_file\.url', r"url_for('media', filename=\1.lesson_file) if \1.lesson_file else ''"),
    
    # Date filters - basic conversion
    (r"\|date:'([^']+)'", r".strftime('\1') if ... else 'N/A'"),
    
    # truncatewords filter
    (r"\|truncatewords:(\d+)", r".split()[:\1]|join(' ')"),
]

def fix_template(file_path):
    """Fix Django syntax in a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Apply all conversions
        for pattern, replacement in CONVERSIONS:
            content = re.sub(pattern, replacement, content)
        
        # Fix common course detail URL patterns
        content = re.sub(
            r"{%\s*url\s+'courses:course_detail'\s+course\.pk\s*%}",
            r"{{ url_for('course_detail', course_id=course.id) }}",
            content
        )
        content = re.sub(
            r"{%\s*url\s+'courses:course_detail'\s+(\w+)\.pk\s*%}",
            r"{{ url_for('course_detail', course_id=\1.id) }}",
            content
        )
        
        # Fix lesson detail URL patterns
        content = re.sub(
            r"{%\s*url\s+'lessons:lesson_detail'\s+lesson\.pk\s*%}",
            r"{{ url_for('lesson_detail', lesson_id=lesson.id) }}",
            content
        )
        content = re.sub(
            r"{%\s*url\s+'lessons:lesson_detail'\s+(\w+)\.pk\s*%}",
            r"{{ url_for('lesson_detail', lesson_id=\1.id) }}",
            content
        )
        
        # Only write if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all template files"""
    template_files = list(TEMPLATE_DIR.rglob('*.html'))
    print(f"Found {len(template_files)} template files")
    
    fixed = 0
    for template_file in template_files:
        if fix_template(template_file):
            print(f"Fixed: {template_file.relative_to(TEMPLATE_DIR)}")
            fixed += 1
    
    print(f"\nFixed {fixed} template files")

if __name__ == '__main__':
    main()

