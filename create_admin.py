#!/usr/bin/env python3
"""
Script to create an admin user for the LMS system.

Usage:
    python create_admin.py
    python create_admin.py --username admin --email admin@example.com --password admin123
"""

import sys
import os
import argparse

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from backend.models import db, User


def create_admin(username=None, email=None, password=None, interactive=True):
    """Create an admin user."""
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print(f"⚠️  Admin user already exists: {existing_admin.username}")
            response = input("Do you want to create another admin? (y/N): ")
            if response.lower() != 'y':
                print("❌ Admin creation cancelled.")
                return
        
        # Get user input if not provided
        if interactive:
            if not username:
                username = input("Enter admin username: ").strip()
                if not username:
                    print("❌ Username is required!")
                    return
            
            if not email:
                email = input("Enter admin email: ").strip()
                if not email:
                    print("❌ Email is required!")
                    return
            
            if not password:
                password = input("Enter admin password (min 8 characters): ").strip()
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters long!")
                    return
                password_confirm = input("Confirm admin password: ").strip()
                if password != password_confirm:
                    print("❌ Passwords do not match!")
                    return
        else:
            if not username or not email or not password:
                print("❌ Username, email, and password are required!")
                return
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            print(f"❌ Username '{username}' already exists!")
            return
        
        if User.query.filter_by(email=email).first():
            print(f"❌ Email '{email}' already exists!")
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"   Role: Administrator")
        print(f"\n📝 You can now login at: http://localhost:5000/accounts/login")
        print(f"   Admin panel: http://localhost:5000/admin")


def main():
    parser = argparse.ArgumentParser(description='Create an admin user for LMS')
    parser.add_argument('--username', type=str, help='Admin username')
    parser.add_argument('--email', type=str, help='Admin email')
    parser.add_argument('--password', type=str, help='Admin password')
    parser.add_argument('--non-interactive', action='store_true', 
                       help='Run in non-interactive mode (requires --username, --email, --password)')
    
    args = parser.parse_args()
    
    interactive = not args.non_interactive
    create_admin(
        username=args.username,
        email=args.email,
        password=args.password,
        interactive=interactive
    )


if __name__ == '__main__':
    main()

