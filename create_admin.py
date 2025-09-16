#!/usr/bin/env python3
"""
Script to create an admin superuser for Youth Club Community
Run this script to create an admin user with full privileges
"""

import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def create_admin_user():
    """Create an admin superuser"""
    
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@youthclub.com').first()
        if existing_admin:
            print("❌ Admin user already exists!")
            print(f"   Email: {existing_admin.email}")
            print(f"   Name: {existing_admin.full_name}")
            print(f"   Admin: {existing_admin.is_admin}")
            print(f"   Active: {existing_admin.is_active}")
            
            response = input("\nDo you want to update the existing admin? (y/N): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                return
            
            # Update existing admin
            existing_admin.is_admin = True
            existing_admin.is_active = True
            existing_admin.is_verified = True
            existing_admin.user_type = 'member'
            existing_admin.full_name = 'Admin User'
            existing_admin.university = 'System Administration'
            existing_admin.university_country = 'Global'
            existing_admin.major = 'System Administration'
            existing_admin.bio = 'System Administrator for Youth Club Community'
            
            # Update password
            new_password = input("Enter new password for admin (or press Enter to keep current): ").strip()
            if new_password:
                existing_admin.set_password(new_password)
                print("✅ Password updated!")
            
            db.session.commit()
            print("✅ Admin user updated successfully!")
            return
        
        # Get admin details
        print("🔧 Creating Admin Superuser for Youth Club Community")
        print("=" * 50)
        
        email = input("Enter admin email (default: admin@youthclub.com): ").strip()
        if not email:
            email = 'admin@youthclub.com'
        
        full_name = input("Enter admin full name (default: Admin User): ").strip()
        if not full_name:
            full_name = 'Admin User'
        
        password = input("Enter admin password: ").strip()
        if not password:
            print("❌ Password is required!")
            return
        
        confirm_password = input("Confirm admin password: ").strip()
        if password != confirm_password:
            print("❌ Passwords do not match!")
            return
        
        # Create admin user
        admin_user = User(
            email=email,
            full_name=full_name,
            user_type='member',  # Set as member type but with admin privileges
            university='System Administration',
            university_country='Global',
            major='System Administration',
            bio='System Administrator for Youth Club Community',
            is_admin=True,
            is_active=True,
            is_verified=True,
            date_joined=datetime.utcnow()
        )
        
        # Set password
        admin_user.set_password(password)
        
        # Add to database
        db.session.add(admin_user)
        db.session.commit()
        
        print("\n✅ Admin superuser created successfully!")
        print("=" * 50)
        print(f"📧 Email: {admin_user.email}")
        print(f"👤 Name: {admin_user.full_name}")
        print(f"🔑 Admin: {admin_user.is_admin}")
        print(f"✅ Active: {admin_user.is_active}")
        print(f"✅ Verified: {admin_user.is_verified}")
        print(f"📅 Created: {admin_user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🌐 You can now login at: http://localhost:5001/login")
        print("🔧 Admin panel available at: http://localhost:5001/admin")

def list_users():
    """List all users in the database"""
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ No users found in the database.")
            return
        
        print(f"\n📊 Database contains {len(users)} user(s):")
        print("=" * 80)
        print(f"{'ID':<3} {'Email':<25} {'Name':<20} {'Type':<10} {'Admin':<6} {'Active':<6}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<3} {user.email:<25} {user.full_name or 'N/A':<20} {user.user_type:<10} {user.is_admin:<6} {user.is_active:<6}")
        
        print("=" * 80)

def main():
    """Main function"""
    
    print("🚀 Youth Club Community - Admin Management")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Create admin superuser")
        print("2. List all users")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            create_admin_user()
        elif choice == '2':
            list_users()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
