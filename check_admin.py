#!/usr/bin/env python3
"""
Script to check admin users in the database
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def check_admin_users():
    """Check admin users in the database"""
    
    with app.app_context():
        # Get all admin users
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("❌ No admin users found in the database.")
            return
        
        print(f"🔧 Found {len(admin_users)} admin user(s):")
        print("=" * 80)
        print(f"{'ID':<3} {'Email':<30} {'Name':<20} {'Active':<6} {'Verified':<8}")
        print("-" * 80)
        
        for admin in admin_users:
            print(f"{admin.id:<3} {admin.email:<30} {admin.full_name or 'N/A':<20} {admin.is_active:<6} {admin.is_verified:<8}")
        
        print("=" * 80)
        
        # Get total user count
        total_users = User.query.count()
        print(f"\n📊 Total users in database: {total_users}")
        
        # Get active users count
        active_users = User.query.filter_by(is_active=True).count()
        print(f"✅ Active users: {active_users}")
        
        # Get members count
        members = User.query.filter_by(user_type='member').count()
        print(f"👥 Members: {members}")
        
        # Get companies count
        companies = User.query.filter_by(user_type='company').count()
        print(f"🏢 Companies: {companies}")

if __name__ == '__main__':
    check_admin_users()
