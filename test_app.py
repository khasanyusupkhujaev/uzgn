import pytest
import os
import tempfile
from app import app, db, User

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_index_page(client):
    """Test the index page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Youth Club' in response.data

def test_register_page(client):
    """Test the registration page loads correctly"""
    response = client.get('/register/member')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_login_page(client):
    """Test the login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_members_page(client):
    """Test the members page loads correctly"""
    response = client.get('/members')
    assert response.status_code == 200
    assert b'Our Community Members' in response.data

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/register/member', data={
        'email': 'test@example.com',
        'password': 'testpassword123',
        'confirm_password': 'testpassword123',
        'full_name': 'Test User',
        'university': 'Test University',
        'university_country': 'Test Country',
        'major': 'Test Major',
        'start_date': '09-2020',
        'end_date': '06-2024'
    })
    
    # Should redirect to login page
    assert response.status_code == 302
    
    # Check if user was created
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.full_name == 'Test User'

def test_user_login(client):
    """Test user login"""
    # First create a user
    user = User(
        email='test@example.com',
        full_name='Test User',
        user_type='member',
        university='Test University',
        university_country='Test Country',
        major='Test Major',
        start_date='09-2020',
        end_date='06-2024'
    )
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()
    
    # Test login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword123'
    })
    
    # Should redirect to dashboard
    assert response.status_code == 302

def test_admin_required(client):
    """Test admin-only routes are protected"""
    response = client.get('/admin')
    assert response.status_code == 302  # Redirect to login

def test_forgot_password_page(client):
    """Test forgot password page loads"""
    response = client.get('/forgot-password')
    assert response.status_code == 200
    assert b'Forgot Password' in response.data

if __name__ == '__main__':
    pytest.main([__file__])
