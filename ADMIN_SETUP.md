# Admin Setup Guide

This guide explains how to create an admin superuser for the Youth Club Community application.

## Method 1: Using the Python Script (Recommended)

Run the interactive script to create an admin user:

```bash
cd /Users/khasanyusupkhuja/Desktop/Personal/youthclub
python create_admin.py
```

The script will:
- Prompt you for admin email, name, and password
- Check if an admin already exists
- Create the admin user with full privileges
- Show you the created user details

## Method 2: Using Flask CLI

You can also use the Flask CLI command:

```bash
cd /Users/khasanyusupkhuja/Desktop/Personal/youthclub
flask create-admin
```

## Method 3: Direct Database Creation

If you prefer to create the admin directly in code, you can run this in a Python shell:

```python
from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Create admin user
    admin = User(
        email='admin@youthclub.com',
        full_name='Admin User',
        user_type='member',
        university='System Administration',
        university_country='Global',
        major='System Administration',
        bio='System Administrator',
        is_admin=True,
        is_active=True,
        is_verified=True,
        date_joined=datetime.utcnow()
    )
    
    admin.set_password('your_password_here')
    
    db.session.add(admin)
    db.session.commit()
    
    print("Admin created successfully!")
```

## Admin Features

Once created, the admin user will have access to:

- **Admin Dashboard**: `/admin` - Overview of all users and statistics
- **User Management**: `/admin/users` - View and manage all users
- **User Details**: `/admin/user/<id>` - View individual user profiles
- **Toggle User Status**: Activate/deactivate users
- **Make Admin**: Promote users to admin status

## Default Admin Credentials

If you use the default settings:
- **Email**: admin@youthclub.com
- **Password**: (whatever you set during creation)

## Security Notes

- Change the default password immediately after creation
- Use a strong, unique password
- Keep admin credentials secure
- Consider using environment variables for production

## Troubleshooting

If you encounter issues:

1. **Database not found**: Make sure the Flask app has been run at least once to create the database
2. **Permission errors**: Ensure you have write permissions to the project directory
3. **Import errors**: Make sure you're running the script from the project root directory

## Accessing Admin Panel

After creating the admin user:

1. Start the Flask application: `python app.py`
2. Go to: http://localhost:5001/login
3. Login with your admin credentials
4. Navigate to: http://localhost:5001/admin

The admin panel provides full control over the Youth Club Community platform.
