# Uzbek Global Network

A web application for a community of talented youth from top universities around the world. Members can register, create profiles, and connect with each other.

## Features

- User registration and authentication
- Member profiles with university and professional information
- Member directory
- Responsive design with Bootstrap
- SQLite database for data storage

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and go to `http://localhost:5000`

## Project Structure

```
youthclub/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── members.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## User Model

The User model includes the following fields:
- Basic info: username, email, password, full_name
- Education: university, graduation_year
- Professional: current_company, current_position, bio
- Social: linkedin_url, github_url
- System: date_joined, is_active

## Next Steps

- Add profile editing functionality
- Implement member search and filtering
- Add messaging system
- Create events and meetups
- Add file upload for profile pictures
- Implement email verification
- Add admin panel
