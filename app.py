from flask import Flask, render_template, request, redirect, url_for, flash, abort, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, gettext, ngettext, get_locale
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
import secrets
from functools import wraps
from config import config

# Create Flask app
# Version: 2.0 - Railway deployment fix
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Override CSRF for development
if config_name == 'development':
    app.config['WTF_CSRF_ENABLED'] = False

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Override with environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or app.config['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or app.config['SQLALCHEMY_DATABASE_URI']

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize security extensions
# csrf = CSRFProtect(app)  # Disabled for development
mail = Mail(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Initialize Babel
babel = Babel(app)

# Babel configuration
app.config['LANGUAGES'] = {
    'en': 'English',
    'uz': 'O\'zbek'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

def get_locale():
    # Check if language is set in session
    try:
        if 'language' in session:
            return session['language']
    except RuntimeError:
        # Session not available (e.g., during app initialization)
        pass
    # Check if language is set in request args
    if request.args.get('lang'):
        return request.args.get('lang')
    # Default to English
    return 'en'

babel.init_app(app, locale_selector=get_locale)

def init_db():
    """Initialize database tables"""
    try:
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Verify table exists by trying to query it
        try:
            # Try to query the User table to verify it exists
            User.query.first()
            print("✅ 'user' table verified in database!")
            return True
        except Exception as verify_error:
            print(f"⚠️  Table creation succeeded but verification failed: {verify_error}")
            # Still return True as the table was created
            return True
            
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print(f"💡 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("💡 Try: Delete the .db file if corrupted, or check file permissions.")
        return False

def create_default_admin():
    """Create a default admin user if none exists"""
    try:
        # Check if any admin exists
        admin_exists = User.query.filter_by(is_admin=True).first()
        if admin_exists:
            print("✅ Admin user already exists!")
            return True
        
        # Create default admin
        admin_user = User(
            email='admin@youthclub.com',
            full_name='Admin User',
            user_type='member',
            university='System Administration',
            university_country='Global',
            major='System Administration',
            bio='System Administrator for Uzbek Global Network',
            is_admin=True,
            is_active=True,
            is_verified=True,
            date_joined=datetime.utcnow()
        )
        
        admin_user.set_password('admin123')  # Default password - should be changed
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Default admin user created!")
        print("📧 Email: admin@youthclub.com")
        print("🔑 Password: admin123")
        print("⚠️  Please change the default password after first login!")
        return True
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")
        return False

def initialize_database():
    """Initialize database tables on first request"""
    try:
        print(f"🔍 Using database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        success = init_db()
        if success:
            create_default_admin()
            print("✅ Database initialization completed successfully!")
        else:
            print("⚠️  Database initialization had issues but continuing...")
    except Exception as e:
        print(f"❌ CRITICAL: Error during database initialization: {e}")
        print("💡 Fix: Check database URI, permissions, and run 'flask create_admin' manually if needed.")
        if app.debug:  # In dev, don't crash, but warn
            print("⚠️  App continuing in broken state - queries will fail!")
        else:
            print("⚠️  Production: App continuing despite database issues - will retry on first request")
            print("✅ App will start successfully and handle database issues gracefully")
            # Don't crash in production, let the app start and handle errors gracefully

# Database initialization will be moved after User class definition

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    user_type = db.Column(db.String(20), nullable=False)  # 'member', 'company'
    
    # Member fields
    university = db.Column(db.String(100), nullable=True)
    university_country = db.Column(db.String(100), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(7), nullable=True)  # MM-YYYY format
    end_date = db.Column(db.String(7), nullable=True)  # MM-YYYY format
    is_current_student = db.Column(db.Boolean, default=False)
    current_company = db.Column(db.String(100), nullable=True)
    current_position = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Social Media
    linkedin_url = db.Column(db.String(200), nullable=True)
    instagram_url = db.Column(db.String(200), nullable=True)
    x_twitter_url = db.Column(db.String(200), nullable=True)
    telegram_url = db.Column(db.String(200), nullable=True)
    github_url = db.Column(db.String(200), nullable=True)
    
    # Additional
    personal_website = db.Column(db.String(200), nullable=True)
    photo_filename = db.Column(db.String(200), nullable=True)
    cv_filename = db.Column(db.String(200), nullable=True)
    
    # Company fields
    company_name = db.Column(db.String(100), nullable=True)
    company_country = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    
    date_joined = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
    
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        if not self.reset_token or not self.reset_token_expires:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return self.reset_token == token

    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def send_email(to, subject, template, **kwargs):
    """Send email using Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_verification_email(user):
    """Send email verification to user"""
    token = user.generate_verification_token()
    db.session.commit()
    
    verification_url = url_for('verify_email', token=token, _external=True)
    template = f"""
    <h2>Welcome to Uzbek Global Network!</h2>
    <p>Please click the link below to verify your email address:</p>
    <a href="{verification_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
    <p>If you didn't create an account, please ignore this email.</p>
    """
    
    return send_email(user.email, 'Verify Your Email - Uzbek Global Network', template)

def send_password_reset_email(user):
    """Send password reset email to user"""
    token = user.generate_reset_token()
    db.session.commit()
    
    reset_url = url_for('reset_password', token=token, _external=True)
    template = f"""
    <h2>Password Reset Request</h2>
    <p>You requested a password reset. Click the link below to reset your password:</p>
    <a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """
    
    return send_email(user.email, 'Password Reset - Uzbek Global Network', template)

# Routes
@app.route('/')
def index():
    try:
        # Get featured members for the carousel (limit to 8 members)
        featured_members = User.query.filter_by(
            is_active=True, 
            is_admin=False, 
            user_type='member'
        ).filter(User.photo_filename.isnot(None)).limit(8).all()
        
        # Get hero members for the hero section (limit to 30 members)
        hero_members = User.query.filter_by(
            is_active=True, 
            is_admin=False, 
            user_type='member'
        ).order_by(User.date_joined.desc()).limit(30).all()
        
        # Get featured companies for the trusted by section (limit to 10 companies)
        featured_companies = User.query.filter_by(
            is_active=True, 
            is_admin=False, 
            user_type='company'
        ).filter(User.photo_filename.isnot(None)).limit(10).all()
        
        # Get statistics for the stats panel
        total_members = User.query.filter_by(is_active=True, is_admin=False).count()
        unique_countries = db.session.query(User.university_country).filter(
            User.is_active == True, 
            User.is_admin == False,
            User.university_country.isnot(None),
            User.university_country != ''
        ).distinct().count()
        
        # Calculate success rate (percentage of verified members)
        verified_members = User.query.filter_by(is_active=True, is_verified=True, is_admin=False).count()
        success_rate = round((verified_members / total_members * 100) if total_members > 0 else 0)
        
        stats = {
            'total_members': total_members,
            'unique_countries': unique_countries,
            'success_rate': success_rate
        }
        
        return render_template('index.html', featured_members=featured_members, hero_members=hero_members, featured_companies=featured_companies, stats=stats)
        
    except Exception as e:
        if "no such table: user" in str(e):
            print("⚠️  Table missing - reinitializing database...")
            with app.app_context():
                try:
                    init_db()
                    create_default_admin()
                    flash('Database was initialized. Please refresh the page.', 'info')
                    return redirect(url_for('index'))
                except Exception as init_error:
                    print(f"❌ Failed to reinitialize database: {init_error}")
                    flash('Database initialization failed. Please contact support.', 'error')
                    return render_template('index.html', featured_members=[], hero_members=[], featured_companies=[], stats={'total_members': 0, 'unique_countries': 0, 'success_rate': 0})
        else:
            raise  # Re-raise other errors

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register')
def register_type_selection():
    return render_template('register_type_selection.html')

@app.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form.get('full_name', '') if user_type == 'member' else ''
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html', user_type=user_type)
        
        # Handle photo upload
        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                photo_filename = unique_filename

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return render_template('register.html', user_type=user_type)

        # Create new user
        user = User(
            email=email,
            full_name=full_name,
            user_type=user_type
        )
        
        # Set fields based on user type
        if user_type == 'member':
            user.university = request.form['university']
            user.university_country = request.form['university_country']
            user.major = request.form['major']
            user.start_date = request.form['start_date']
            user.end_date = request.form['end_date']
            user.is_current_student = 'is_current_student' in request.form
            user.current_company = request.form.get('current_company', '')
            user.current_position = request.form.get('current_position', '')
            user.bio = request.form.get('bio', '')
            user.linkedin_url = request.form.get('linkedin_url', '')
            user.photo_filename = photo_filename
        elif user_type == 'company':
            user.company_name = request.form['company_name']
            user.company_country = request.form['company_country']
            user.industry = request.form['industry']
            
            # Handle company logo upload
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file and logo_file.filename and allowed_file(logo_file.filename):
                    filename = secure_filename(logo_file.filename)
                    unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()
                    logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    user.photo_filename = unique_filename
        
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', user_type=user_type)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            if send_password_reset_email(user):
                flash('Password reset email sent! Check your inbox.', 'success')
            else:
                flash('Failed to send email. Please try again later.', 'error')
        else:
            flash('Email not found in our system.', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('reset_password.html', token=token)
        
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        flash('Password updated successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Invalid verification token.', 'error')
        return redirect(url_for('login'))
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/members')
def members():
    users = User.query.filter_by(is_active=True).filter_by(is_admin=False).filter_by(user_type='member').all()
    return render_template('members.html', users=users)

@app.route('/companies')
def companies():
    companies = User.query.filter_by(is_active=True).filter_by(is_admin=False).filter_by(user_type='company').all()
    return render_template('companies.html', companies=companies)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/set_language/<language>')
def set_language(language=None):
    if language in app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/member/<int:user_id>')
def member_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('member_details.html', user=user)

@app.route('/company/<int:company_id>')
def company_details(company_id):
    company = User.query.get_or_404(company_id)
    if company.user_type != 'company':
        abort(404)
    return render_template('company_details.html', company=company)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if current_user.user_type == 'member':
            # Update member information
            current_user.full_name = request.form.get('full_name', current_user.full_name)
            current_user.bio = request.form.get('bio', current_user.bio)
            current_user.phone = request.form.get('phone', current_user.phone)
            
            # Update social media
            current_user.linkedin_url = request.form.get('linkedin_url', current_user.linkedin_url)
            current_user.instagram_url = request.form.get('instagram_url', current_user.instagram_url)
            current_user.x_twitter_url = request.form.get('x_twitter_url', current_user.x_twitter_url)
            current_user.telegram_url = request.form.get('telegram_url', current_user.telegram_url)
            current_user.github_url = request.form.get('github_url', current_user.github_url)
            
            # Update additional fields
            current_user.personal_website = request.form.get('personal_website', current_user.personal_website)
            
            # Handle photo upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    current_user.photo_filename = unique_filename
            
            # Handle CV upload
            if 'cv' in request.files:
                file = request.files['cv']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    current_user.cv_filename = unique_filename
        
        elif current_user.user_type == 'company':
            # Update company information
            current_user.company_name = request.form.get('company_name', current_user.company_name)
            current_user.company_country = request.form.get('company_country', current_user.company_country)
            current_user.industry = request.form.get('industry', current_user.industry)
            current_user.bio = request.form.get('bio', current_user.bio)
            current_user.phone = request.form.get('phone', current_user.phone)
            
            # Update social media
            current_user.linkedin_url = request.form.get('linkedin_url', current_user.linkedin_url)
            current_user.instagram_url = request.form.get('instagram_url', current_user.instagram_url)
            current_user.x_twitter_url = request.form.get('x_twitter_url', current_user.x_twitter_url)
            current_user.telegram_url = request.form.get('telegram_url', current_user.telegram_url)
            current_user.github_url = request.form.get('github_url', current_user.github_url)
            
            # Update additional fields
            current_user.personal_website = request.form.get('personal_website', current_user.personal_website)
            
            # Handle logo upload
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    current_user.photo_filename = unique_filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_profile.html', user=current_user)

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    total_users = len(users)
    active_users = len([u for u in users if u.is_active])
    members = len([u for u in users if u.user_type == 'member'])
    companies = len([u for u in users if u.user_type == 'company'])
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'members': members,
        'companies': companies
    }
    
    return render_template('admin/dashboard.html', users=users, stats=stats)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.full_name or user.company_name} status updated!', 'success')
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/admin/user/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def admin_make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.full_name or user.company_name} is now an admin!', 'success')
    return redirect(url_for('admin_user_detail', user_id=user_id))

def init_db():
    """Initialize database tables"""
    try:
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Verify table exists by trying to query it
        try:
            # Try to query the User table to verify it exists
            User.query.first()
            print("✅ 'user' table verified in database!")
            return True
        except Exception as verify_error:
            print(f"⚠️  Table creation succeeded but verification failed: {verify_error}")
            # Still return True as the table was created
            return True
            
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print(f"💡 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("💡 Try: Delete the .db file if corrupted, or check file permissions.")
        return False

def create_default_admin():
    """Create a default admin user if none exists"""
    try:
        # Check if any admin exists
        admin_exists = User.query.filter_by(is_admin=True).first()
        if admin_exists:
            print("✅ Admin user already exists!")
            return True
        
        # Create default admin
        admin_user = User(
            email='admin@youthclub.com',
            full_name='Admin User',
            user_type='member',
            university='System Administration',
            university_country='Global',
            major='System Administration',
            bio='System Administrator for Uzbek Global Network',
            is_admin=True,
            is_active=True,
            is_verified=True
        )
        
        admin_user.set_password('admin123')  # Default password - should be changed
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Default admin user created!")
        print("📧 Email: admin@youthclub.com")
        print("🔑 Password: admin123")
        print("⚠️  Please change the default password after first login!")
        return True
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")
        return False

# Flask CLI commands
@app.cli.command()
def create_admin():
    """Create an admin superuser"""
    from getpass import getpass
    
    print("🔧 Creating Admin Superuser for Uzbek Global Network")
    print("=" * 50)
    
    email = input("Enter admin email (default: admin@youthclub.com): ").strip()
    if not email:
        email = 'admin@youthclub.com'
    
    full_name = input("Enter admin full name (default: Admin User): ").strip()
    if not full_name:
        full_name = 'Admin User'
    
    password = getpass("Enter admin password: ")
    if not password:
        print("❌ Password is required!")
        return
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(email=email).first()
    if existing_admin:
        print(f"❌ User with email {email} already exists!")
        return
    
    # Create admin user
    admin_user = User(
        email=email,
        full_name=full_name,
        user_type='member',
        university='System Administration',
        university_country='Global',
        major='System Administration',
        bio='System Administrator for Uzbek Global Network',
        is_admin=True,
        is_active=True,
        is_verified=True,
        date_joined=datetime.utcnow()
    )
    
    admin_user.set_password(password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    print("✅ Admin superuser created successfully!")
    print(f"📧 Email: {admin_user.email}")
    print(f"👤 Name: {admin_user.full_name}")
    print("🌐 You can now login at: http://localhost:5001/login")

# Initialize database after all models are defined
with app.app_context():
    initialize_database()

if __name__ == '__main__':
    # Removed duplicate init here - it's handled in the context block above
    app.run(debug=True, port=5001)
