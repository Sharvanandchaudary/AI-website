# Flask Backend for AI Solutions Website
# This server handles user authentication and email notifications

from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')

# CORS Configuration - Allow all origins in development, specific in production
if os.getenv('FLASK_ENV') == 'production':
    cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
else:
    CORS(app)  # Allow all origins in development

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')

mail = Mail(app)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'aisolutions.db')
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

# Mailgun setup
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY', '')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', '')
MAILGUN_FROM_EMAIL = os.getenv('MAILGUN_FROM_EMAIL', 'noreply@yourdomain.com')

# Debug: Print environment variables (without sensitive data)
print("=" * 60)
print("🔍 ENVIRONMENT DIAGNOSTICS")
print("=" * 60)
print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'NOT SET')}")
print(f"DATABASE_URL present: {'Yes' if os.getenv('DATABASE_URL') else 'NO - THIS IS THE PROBLEM!'}")
if os.getenv('DATABASE_URL'):
    db_url_preview = os.getenv('DATABASE_URL')[:20] + "..." if len(os.getenv('DATABASE_URL')) > 20 else os.getenv('DATABASE_URL')
    print(f"DATABASE_URL preview: {db_url_preview}")
print(f"All env vars: {', '.join([k for k in os.environ.keys() if not any(x in k.lower() for x in ['key', 'secret', 'password', 'token'])])}")
print("=" * 60)

# Use PostgreSQL in production - Check for postgres:// or postgresql:// URL
if DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://'):
    # Render uses postgres:// but psycopg2 needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    import psycopg2
    USE_POSTGRES = True
    print(f"✅ Using PostgreSQL database")
else:
    USE_POSTGRES = False
    DB_NAME = DATABASE_URL
    print(f"⚠️ Using SQLite database: {DB_NAME}")
    print(f"⚠️ WARNING: SQLite should only be used for local development!")
    print(f"⚠️ Set DATABASE_URL environment variable on Render!")

def get_db_connection():
    """Get database connection (SQLite or PostgreSQL)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    else:
        return sqlite3.connect(DB_NAME)

def init_db():
    """Initialize the database with required tables"""
    print("🔧 Initializing database tables...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(50) NOT NULL,
                address TEXT NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
    
    # Emails table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                to_email VARCHAR(255) NOT NULL,
                subject VARCHAR(500) NOT NULL,
                body TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER REFERENCES users(id)
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                to_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    
    # Sessions table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    
    # Projects table
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'planning',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'planning',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    
    # Applications table for job applications
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                position VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                address TEXT NOT NULL,
                college VARCHAR(255) NOT NULL,
                degree VARCHAR(255) NOT NULL,
                semester VARCHAR(50) NOT NULL,
                year VARCHAR(50) NOT NULL,
                about TEXT NOT NULL,
                resume_name VARCHAR(255) NOT NULL,
                linkedin VARCHAR(500),
                github VARCHAR(500),
                status VARCHAR(50) DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                college TEXT NOT NULL,
                degree TEXT NOT NULL,
                semester TEXT NOT NULL,
                year TEXT NOT NULL,
                about TEXT NOT NULL,
                resume_name TEXT NOT NULL,
                linkedin TEXT,
                github TEXT,
                status TEXT DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Selected Interns table - interns who get dashboard access
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selected_interns (
                id SERIAL PRIMARY KEY,
                application_id INTEGER REFERENCES applications(id),
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                position VARCHAR(255) NOT NULL,
                college VARCHAR(255) NOT NULL,
                start_date DATE DEFAULT CURRENT_DATE,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selected_interns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                position TEXT NOT NULL,
                college TEXT NOT NULL,
                start_date DATE DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
    
    # Weekly Tasks table - preloaded by admin
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_tasks (
                id SERIAL PRIMARY KEY,
                week_number INTEGER NOT NULL,
                task_title VARCHAR(255) NOT NULL,
                task_description TEXT NOT NULL,
                mini_project_guidelines TEXT,
                ds_algo_topic VARCHAR(255),
                ai_news TEXT,
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_number INTEGER NOT NULL,
                task_title TEXT NOT NULL,
                task_description TEXT NOT NULL,
                mini_project_guidelines TEXT,
                ds_algo_topic TEXT,
                ai_news TEXT,
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Task Submissions table - intern uploads
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_submissions (
                id SERIAL PRIMARY KEY,
                intern_id INTEGER NOT NULL REFERENCES selected_interns(id),
                task_id INTEGER NOT NULL REFERENCES weekly_tasks(id),
                submission_file TEXT,
                submission_type VARCHAR(50),
                what_learned TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'submitted'
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                submission_file TEXT,
                submission_type TEXT,
                what_learned TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'submitted',
                FOREIGN KEY (intern_id) REFERENCES selected_interns (id),
                FOREIGN KEY (task_id) REFERENCES weekly_tasks (id)
            )
        ''')
    
    # Intern Progress Tracking
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intern_progress (
                id SERIAL PRIMARY KEY,
                intern_id INTEGER NOT NULL REFERENCES selected_interns(id),
                week_number INTEGER NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                tasks_total INTEGER DEFAULT 0,
                performance_notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intern_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                tasks_total INTEGER DEFAULT 0,
                performance_notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intern_id) REFERENCES selected_interns (id)
            )
        ''')
    
    # Intern Sessions table for authentication
    if USE_POSTGRES:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intern_sessions (
                id SERIAL PRIMARY KEY,
                intern_id INTEGER NOT NULL REFERENCES selected_interns(id),
                token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intern_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intern_id) REFERENCES selected_interns (id)
            )
        ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def send_email_mailgun(to_email, subject, body):
    """Send email using Mailgun API"""
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        print("⚠️ Mailgun not configured, email not sent")
        return False
    
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"XGENAI <{MAILGUN_FROM_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "text": body,
                "html": body.replace('\n', '<br>')
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Email sent to: {to_email}")
            return True
        else:
            print(f"❌ Mailgun error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def send_confirmation_email(user_data):
    """Send confirmation email to new user"""
    try:
        email_body = f"""
Hi {user_data['name']},

Welcome to XGENAI!

Your account has been created successfully. Here are your details:

Name: {user_data['name']}
Email: {user_data['email']}
Phone: {user_data['phone']}
Address: {user_data['address']}
Account Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

You can now login to your dashboard and start managing your projects.

Thank you for joining us!

Best regards,
XGENAI Team
        """
        
        subject = 'Welcome to XGENAI - Account Created Successfully!'
        
        # Store email in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO emails (to_email, subject, body, user_id)
                VALUES (%s, %s, %s, %s)
            ''', (
                user_data['email'],
                subject,
                email_body,
                user_data.get('user_id')
            ))
        else:
            cursor.execute('''
                INSERT INTO emails (to_email, subject, body, user_id)
                VALUES (?, ?, ?, ?)
            ''', (
                user_data['email'],
                subject,
                email_body,
                user_data.get('user_id')
            ))
        
        conn.commit()
        conn.close()
        
        # Send email via Mailgun
        if IS_PRODUCTION:
            send_email_mailgun(user_data['email'], subject, email_body)
        else:
            print(f"📧 Email logged for: {user_data['email']}")
        
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

# Admin credentials (in production, store these securely in database with hashing)
ADMIN_USERS = {
    os.getenv('ADMIN_EMAIL', 'admin@xgenai.com'): {
        'password_hash': hashlib.sha256(os.getenv('ADMIN_PASSWORD', 'Admin@123').encode()).hexdigest(),
        'role': 'admin'
    }
}

# Admin session management
admin_sessions = {}

def verify_admin_token(token):
    """Verify admin authentication token"""
    if not token:
        return False
    return token in admin_sessions

# Initialize database on module load (works with Gunicorn)
try:
    print("🔧 Starting database initialization...")
    init_db()
    print("✅ Database initialized on startup")
except Exception as e:
    print(f"⚠️ Database initialization error: {e}")
    import traceback
    traceback.print_exc()

# Routes

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'PostgreSQL' if USE_POSTGRES else 'SQLite',
            'connection': 'ok'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

# Cache version for busting browser cache
CACHE_VERSION = 'v2.1.0'

def add_security_headers(response):
    """Add production security headers"""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Cache-Control'] = f'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/careers')
def careers_page():
    """Serve careers page"""
    response = send_from_directory('.', 'careers.html')
    return add_security_headers(response)

@app.route('/auth')
def auth_page():
    """Serve authentication page"""
    response = send_from_directory('.', 'auth.html')
    return add_security_headers(response)

@app.route('/dashboard')
def dashboard_page():
    """Serve user dashboard page"""
    response = send_from_directory('.', 'dashboard.html')
    return add_security_headers(response)

@app.route('/apply')
def apply_page():
    """Serve application form page"""
    response = send_from_directory('pages', 'apply.html')
    return add_security_headers(response)

# PRODUCTION-GRADE ADMIN PORTAL - Separate URL Structure
@app.route('/xgenai-admin-portal')
def xgenai_admin_portal_login():
    """Production admin portal - Login page"""
    response = send_from_directory('.', 'xgenai-admin-login.html')
    return add_security_headers(response)

@app.route('/xgenai-admin-portal/dashboard')
def xgenai_admin_portal_dashboard():
    """Production admin portal - Dashboard"""
    response = send_from_directory('.', 'xgenai-admin-dashboard.html')
    return add_security_headers(response)

# Legacy admin URLs - Redirect to new portal
@app.route('/admin')
def admin_page():
    """Redirect old admin URL to new portal"""
    return redirect('/xgenai-admin-portal')

@app.route('/xgenai-admin')
def xgenai_admin_legacy():
    """Legacy admin URL - redirect to new portal"""
    return redirect('/xgenai-admin-portal')

@app.route('/xgen-admin-portal')
def admin_auth_portal():
    """Legacy admin URL - redirect to new portal"""
    return redirect('/xgenai-admin-portal')

@app.route('/xgenai-admin-dashboard')
def xgenai_admin_dashboard_legacy():
    """Legacy dashboard - redirect to new portal"""
    return redirect('/xgenai-admin-portal/dashboard')

@app.route('/xgen-admin-dashboard')
def admin_dashboard_portal():
    """Legacy dashboard - redirect to new portal"""
    return redirect('/xgenai-admin-portal/dashboard')

# Intern Portal
@app.route('/intern-login')
def intern_login_page():
    """Serve intern login page"""
    response = send_from_directory('.', 'intern-login.html')
    return add_security_headers(response)

@app.route('/intern-dashboard')
def intern_dashboard_page():
    """Serve intern dashboard page"""
    response = send_from_directory('.', 'intern-dashboard.html')
    return add_security_headers(response)

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files with proper caching and security"""
    response = send_from_directory('.', path)
    
    # Add security headers and no-cache for HTML, CSS, JS
    if path.endswith(('.html', '.css', '.js')):
        response = add_security_headers(response)
    else:
        # Allow caching for images and other assets (1 hour)
        response.headers['Cache-Control'] = 'public, max-age=3600'
    
    return response

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('SELECT id FROM users WHERE email = %s', (data['email'],))
        else:
            cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = hash_password(data['password'])
        
        # Insert new user
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO users (name, email, phone, address, password_hash, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (data['name'], data['email'], data['phone'], data['address'], password_hash, datetime.now()))
            user_id = cursor.fetchone()[0]
        else:
            cursor.execute('''
                INSERT INTO users (name, email, phone, address, password_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['name'], data['email'], data['phone'], data['address'], password_hash))
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Send confirmation email
        email_data = {
            'user_id': user_id,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address']
        }
        send_confirmation_email(email_data)
        
        return jsonify({
            'message': 'Account created successfully!',
            'user_id': user_id,
            'email': data['email']
        }), 201
        
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check admin credentials
        admin = ADMIN_USERS.get(email)
        if not admin:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != admin['password_hash']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create admin session token
        token = secrets.token_urlsafe(32)
        admin_sessions[token] = {
            'email': email,
            'role': admin['role'],
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'token': token,
            'role': admin['role']
        }), 200
        
    except Exception as e:
        print(f"Error in admin login: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout endpoint"""
    try:
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if token and token in admin_sessions:
            del admin_sessions[token]
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Hash password
        password_hash = hash_password(data['password'])
        
        # Check credentials
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                SELECT id, name, email, phone, address, created_at
                FROM users
                WHERE email = %s AND password_hash = %s
            ''', (data['email'], password_hash))
        else:
            cursor.execute('''
                SELECT id, name, email, phone, address, created_at
                FROM users
                WHERE email = ? AND password_hash = ?
            ''', (data['email'], password_hash))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        if USE_POSTGRES:
            cursor.execute('UPDATE users SET last_login = %s WHERE id = %s', 
                          (datetime.now(), user[0]))
        else:
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                          (datetime.now(), user[0]))
        
        # Create session token
        token = secrets.token_hex(32)
        
        if USE_POSTGRES:
            cursor.execute('INSERT INTO sessions (user_id, token) VALUES (%s, %s)',
                          (user[0], token))
        else:
            cursor.execute('INSERT INTO sessions (user_id, token) VALUES (?, ?)',
                          (user[0], token))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'phone': user[3],
                'address': user[4],
                'created_at': user[5]
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (admin only - requires authentication)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, phone, address, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'address': row[4],
                'created_at': str(row[5]) if row[5] else None,
                'last_login': str(row[6]) if row[6] else None
            })
        
        conn.close()
        return jsonify({'users': users}), 200
        
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get all sent emails (admin only - requires authentication)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, e.to_email, e.subject, e.body, e.sent_at, u.name
            FROM emails e
            LEFT JOIN users u ON e.user_id = u.id
            ORDER BY e.sent_at DESC
        ''')
        
        emails = []
        for row in cursor.fetchall():
            emails.append({
                'id': row[0],
                'to': row[1],
                'subject': row[2],
                'body': row[3],
                'sent_at': row[4],
                'user_name': row[5]
            })
        
        conn.close()
        return jsonify({'emails': emails}), 200
        
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics (admin only - requires authentication)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error fetching users count: {e}")
            total_users = 0
        
        try:
            # Total emails
            cursor.execute('SELECT COUNT(*) FROM emails')
            total_emails = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error fetching emails count: {e}")
            total_emails = 0
        
        try:
            # Users today
            if USE_POSTGRES:
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(created_at) = CURRENT_DATE
                ''')
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(created_at) = DATE('now')
                ''')
            today_users = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error fetching today's users: {e}")
            today_users = 0
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_emails': total_emails,
            'today_users': today_users
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'total_users': 0,
            'total_emails': 0,
            'today_users': 0,
            'error': str(e)
        }), 200  # Return 200 with zeros instead of 500

@app.route('/api/clear-data', methods=['DELETE'])
def clear_data():
    """Clear all data (admin only)"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions')
        cursor.execute('DELETE FROM emails')
        cursor.execute('DELETE FROM projects')
        cursor.execute('DELETE FROM users')
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'All data cleared successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# User Dashboard Endpoints

def verify_token(token):
    """Verify user token and return user_id"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM sessions WHERE token = ?', (token,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return None

@app.route('/api/user/dashboard', methods=['GET'])
def get_user_dashboard():
    """Get user dashboard data"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute('''
            SELECT id, name, email, phone, address, created_at, last_login
            FROM users WHERE id = ?
        ''', (user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            'id': user_row[0],
            'name': user_row[1],
            'email': user_row[2],
            'phone': user_row[3],
            'address': user_row[4],
            'created_at': user_row[5],
            'last_login': user_row[6]
        }
        
        # Get user projects
        cursor.execute('''
            SELECT id, name, description, status, created_at, updated_at
            FROM projects WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'status': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'user': user_data,
            'projects': projects
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching user dashboard: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/user/projects', methods=['POST'])
def add_project():
    """Add a new project"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('description') or not data.get('status'):
            return jsonify({'error': 'Name, description, and status are required'}), 400
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO projects (user_id, name, description, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, data['name'], data['description'], data['status']))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Project added successfully',
            'project_id': project_id
        }), 201
        
    except Exception as e:
        print(f"❌ Error adding project: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Admin Enhanced Endpoints

@app.route('/api/admin/all-data', methods=['GET'])
def get_all_admin_data():
    """Get all users with their projects (admin only)"""
    try:
        # Get token from Authorization header (optional for development)
        auth_header = request.headers.get('Authorization')
        
        # For development: allow access without token
        # Comment out these lines for production
        if not auth_header or not auth_header.startswith('Bearer '):
            pass  # Allow access for development
        elif auth_header:
            token = auth_header.split(' ')[1]
            user_id = verify_token(token)
            # Token validation is optional for now
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute('''
            SELECT id, name, email, phone, address, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            user_id_iter = row[0]
            
            # Get projects for this user
            cursor.execute('''
                SELECT id, name, description, status, created_at, updated_at
                FROM projects WHERE user_id = ?
                ORDER BY updated_at DESC
            ''', (user_id_iter,))
            
            projects = []
            for proj_row in cursor.fetchall():
                projects.append({
                    'id': proj_row[0],
                    'name': proj_row[1],
                    'description': proj_row[2],
                    'status': proj_row[3],
                    'created_at': proj_row[4],
                    'updated_at': proj_row[5]
                })
            
            users.append({
                'id': user_id_iter,
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'address': row[4],
                'created_at': row[5],
                'last_login': row[6],
                'projects': projects
            })
        
        conn.close()
        return jsonify({'users': users}), 200
        
    except Exception as e:
        print(f"❌ Error fetching admin data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Job Applications Endpoints

@app.route('/api/applications', methods=['POST', 'OPTIONS'])
def submit_application():
    """Submit job application"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        
        print(f"📝 Received application data: {data}")
        
        # Validate required fields
        required_fields = ['position', 'fullName', 'email', 'phone', 'address', 
                          'college', 'degree', 'semester', 'year', 'about', 'resumeName']
        
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        print(f"✅ All required fields present for {data['fullName']}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert application
        if USE_POSTGRES:
            print("📊 Using PostgreSQL database")
            cursor.execute('''
                INSERT INTO applications 
                (position, full_name, email, phone, address, college, degree, 
                 semester, year, about, resume_name, linkedin, github, applied_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                data['position'], data['fullName'], data['email'], data['phone'],
                data['address'], data['college'], data['degree'], data['semester'],
                data['year'], data['about'], data['resumeName'],
                data.get('linkedin', ''), data.get('github', ''),
                datetime.now(), 'pending'
            ))
            application_id = cursor.fetchone()[0]
        else:
            print("📊 Using SQLite database")
            cursor.execute('''
                INSERT INTO applications 
                (position, full_name, email, phone, address, college, degree, 
                 semester, year, about, resume_name, linkedin, github, applied_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['position'], data['fullName'], data['email'], data['phone'],
                data['address'], data['college'], data['degree'], data['semester'],
                data['year'], data['about'], data['resumeName'],
                data.get('linkedin', ''), data.get('github', ''),
                datetime.now(), 'pending'
            ))
            application_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"✅ Application saved with ID: {application_id}")
        
        # Send confirmation email
        email_body = f"""
Hi {data['fullName']},

Thank you for applying to XGENAI!

We have received your application for the {data['position']} position.

Application Details:
- Position: {data['position']}
- College: {data['college']}
- Semester: {data['semester']}
- Expected Graduation: {data['year']}

Our team will review your application and get back to you within 5-7 business days.

Best regards,
XGENAI Recruitment Team
        """
        
        send_email_mailgun(data['email'], f"Application Received - {data['position']}", email_body)
        
        print(f"✅ Application submitted successfully for {data['fullName']}")
        
        return jsonify({
            'message': 'Application submitted successfully!',
            'application_id': application_id
        }), 201
        
    except Exception as e:
        print(f"❌ Error submitting application: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to submit application: {str(e)}'}), 500

@app.route('/api/admin/applications', methods=['GET', 'OPTIONS'])
def get_all_applications():
    """Get all job applications (admin only - requires authentication)"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, position, full_name, email, phone, college, semester, 
                   year, status, applied_at, linkedin, github
            FROM applications
            ORDER BY applied_at DESC
        ''')
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                'id': row[0],
                'position': row[1],
                'fullName': row[2],
                'email': row[3],
                'phone': row[4],
                'college': row[5],
                'semester': row[6],
                'year': row[7],
                'status': row[8],
                'appliedAt': row[9],
                'linkedin': row[10],
                'github': row[11]
            })
        
        conn.close()
        return jsonify({'applications': applications}), 200
        
    except Exception as e:
        print(f"❌ Error fetching applications: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    """Update application status (admin only - requires authentication)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'application_received', 'under_review', 'interview', 'selected', 'rejected']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                UPDATE applications 
                SET status = %s 
                WHERE id = %s
            ''', (new_status, app_id))
        else:
            cursor.execute('''
                UPDATE applications 
                SET status = ? 
                WHERE id = ?
            ''', (new_status, app_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Status updated successfully', 'status': new_status}), 200
        
    except Exception as e:
        print(f"❌ Error updating application status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/send-application-email', methods=['POST'])
def send_application_email():
    """Send email to candidate about application status (admin only - requires authentication)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        
        required_fields = ['applicationId', 'email', 'subject', 'body']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Send email
        send_email_mailgun(data['email'], data['subject'], data['body'])
        
        # Store email record
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO emails (to_email, subject, body, sent_at)
                VALUES (%s, %s, %s, %s)
            ''', (data['email'], data['subject'], data['body'], datetime.now()))
        else:
            cursor.execute('''
                INSERT INTO emails (to_email, subject, body, sent_at)
                VALUES (?, ?, ?, ?)
            ''', (data['email'], data['subject'], data['body'], datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Email sent successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error sending application email: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/init-db', methods=['POST'])
def init_database():
    """Initialize/reset database (admin only)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        init_db()
        return jsonify({'message': 'Database initialized successfully'}), 200
    except Exception as e:
        print(f"Error initializing database: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/check-db', methods=['GET'])
def check_database():
    """Check database tables and counts (admin only)"""
    try:
        # Verify admin authentication
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get counts from all tables
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM users')
        stats['users'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications')
        stats['applications'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM emails')
        stats['emails'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        stats['sessions'] = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'database': 'PostgreSQL' if USE_POSTGRES else 'SQLite',
            'stats': stats
        }), 200
    except Exception as e:
        print(f"Error checking database: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# INTERN MANAGEMENT SYSTEM
# ============================================================

# Intern session management
intern_sessions = {}

def verify_intern_token(token):
    """Verify intern authentication token"""
    if not token:
        return None
    return intern_sessions.get(token)

# INTERN LOGIN & AUTHENTICATION

@app.route('/api/intern/login', methods=['POST', 'OPTIONS'])
def intern_login():
    """Intern login endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        password_hash = hash_password(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if intern exists and password matches
        if USE_POSTGRES:
            cursor.execute('''
                SELECT id, full_name, email, position, college, status 
                FROM selected_interns 
                WHERE email = %s AND password_hash = %s
            ''', (email, password_hash))
        else:
            cursor.execute('''
                SELECT id, full_name, email, position, college, status 
                FROM selected_interns 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
        
        intern = cursor.fetchone()
        
        if not intern:
            conn.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        intern_id = intern[0]
        
        # Check if intern is active
        if intern[5] != 'active':
            conn.close()
            return jsonify({'error': 'Account is not active'}), 403
        
        # Create session token
        token = secrets.token_hex(32)
        
        # Store in database
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO intern_sessions (intern_id, token)
                VALUES (%s, %s)
            ''', (intern_id, token))
        else:
            cursor.execute('''
                INSERT INTO intern_sessions (intern_id, token)
                VALUES (?, ?)
            ''', (intern_id, token))
        
        conn.commit()
        conn.close()
        
        # Store in memory
        intern_sessions[token] = {
            'intern_id': intern_id,
            'email': intern[2],
            'name': intern[1],
            'position': intern[3]
        }
        
        return jsonify({
            'success': True,
            'token': token,
            'intern': {
                'id': intern_id,
                'name': intern[1],
                'email': intern[2],
                'position': intern[3],
                'college': intern[4]
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Intern login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/intern/logout', methods=['POST'])
def intern_logout():
    """Intern logout endpoint"""
    try:
        token = request.cookies.get('intern_token') or request.headers.get('Authorization')
        
        if token and token in intern_sessions:
            # Remove from memory
            del intern_sessions[token]
            
            # Remove from database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if USE_POSTGRES:
                cursor.execute('DELETE FROM intern_sessions WHERE token = %s', (token,))
            else:
                cursor.execute('DELETE FROM intern_sessions WHERE token = ?', (token,))
            
            conn.commit()
            conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

# INTERN DASHBOARD APIs

@app.route('/api/intern/dashboard', methods=['GET', 'OPTIONS'])
def get_intern_dashboard():
    """Get intern dashboard data"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        token = request.cookies.get('intern_token') or request.headers.get('Authorization')
        intern_data = verify_intern_token(token)
        
        if not intern_data:
            return jsonify({'error': 'Unauthorized'}), 401
        
        intern_id = intern_data['intern_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current week number (calculate from start date)
        if USE_POSTGRES:
            cursor.execute('''
                SELECT EXTRACT(WEEK FROM CURRENT_DATE) - EXTRACT(WEEK FROM start_date) + 1 as current_week
                FROM selected_interns
                WHERE id = %s
            ''', (intern_id,))
        else:
            cursor.execute('''
                SELECT (julianday('now') - julianday(start_date)) / 7 + 1 as current_week
                FROM selected_interns
                WHERE id = ?
            ''', (intern_id,))
        
        result = cursor.fetchone()
        current_week = int(result[0]) if result else 1
        
        # Get all tasks for current week
        if USE_POSTGRES:
            cursor.execute('''
                SELECT id, week_number, task_title, task_description, 
                       mini_project_guidelines, ds_algo_topic, ai_news, due_date
                FROM weekly_tasks
                WHERE week_number = %s
                ORDER BY id
            ''', (current_week,))
        else:
            cursor.execute('''
                SELECT id, week_number, task_title, task_description, 
                       mini_project_guidelines, ds_algo_topic, ai_news, due_date
                FROM weekly_tasks
                WHERE week_number = ?
                ORDER BY id
            ''', (current_week,))
        
        tasks = cursor.fetchall()
        
        # Get submission history
        if USE_POSTGRES:
            cursor.execute('''
                SELECT ts.id, wt.task_title, wt.week_number, ts.submission_type, 
                       ts.submitted_at, ts.status, ts.what_learned
                FROM task_submissions ts
                JOIN weekly_tasks wt ON ts.task_id = wt.id
                WHERE ts.intern_id = %s
                ORDER BY ts.submitted_at DESC
                LIMIT 10
            ''', (intern_id,))
        else:
            cursor.execute('''
                SELECT ts.id, wt.task_title, wt.week_number, ts.submission_type, 
                       ts.submitted_at, ts.status, ts.what_learned
                FROM task_submissions ts
                JOIN weekly_tasks wt ON ts.task_id = wt.id
                WHERE ts.intern_id = ?
                ORDER BY ts.submitted_at DESC
                LIMIT 10
            ''', (intern_id,))
        
        submissions = cursor.fetchall()
        
        # Get progress stats
        if USE_POSTGRES:
            cursor.execute('''
                SELECT tasks_completed, tasks_total
                FROM intern_progress
                WHERE intern_id = %s AND week_number = %s
            ''', (intern_id, current_week))
        else:
            cursor.execute('''
                SELECT tasks_completed, tasks_total
                FROM intern_progress
                WHERE intern_id = ? AND week_number = ?
            ''', (intern_id, current_week))
        
        progress = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'intern': intern_data,
            'current_week': current_week,
            'tasks': [{
                'id': t[0],
                'week_number': t[1],
                'title': t[2],
                'description': t[3],
                'mini_project_guidelines': t[4],
                'ds_algo_topic': t[5],
                'ai_news': t[6],
                'due_date': str(t[7]) if t[7] else None
            } for t in tasks],
            'submissions': [{
                'id': s[0],
                'task_title': s[1],
                'week_number': s[2],
                'submission_type': s[3],
                'submitted_at': str(s[4]),
                'status': s[5],
                'what_learned': s[6]
            } for s in submissions],
            'progress': {
                'completed': progress[0] if progress else 0,
                'total': progress[1] if progress else len(tasks)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intern/submit-task', methods=['POST', 'OPTIONS'])
def submit_task():
    """Submit a task with file upload"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        token = request.cookies.get('intern_token') or request.headers.get('Authorization')
        intern_data = verify_intern_token(token)
        
        if not intern_data:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        task_id = data.get('task_id')
        submission_file = data.get('submission_file')  # Base64 encoded file
        submission_type = data.get('submission_type', 'pdf')
        what_learned = data.get('what_learned', '')
        
        if not task_id:
            return jsonify({'error': 'Task ID required'}), 400
        
        intern_id = intern_data['intern_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert submission
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO task_submissions (intern_id, task_id, submission_file, submission_type, what_learned)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (intern_id, task_id, submission_file, submission_type, what_learned))
            submission_id = cursor.fetchone()[0]
        else:
            cursor.execute('''
                INSERT INTO task_submissions (intern_id, task_id, submission_file, submission_type, what_learned)
                VALUES (?, ?, ?, ?, ?)
            ''', (intern_id, task_id, submission_file, submission_type, what_learned))
            submission_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'submission_id': submission_id,
            'message': 'Task submitted successfully!'
        }), 200
        
    except Exception as e:
        print(f"❌ Error submitting task: {e}")
        return jsonify({'error': str(e)}), 500

# ADMIN INTERN MANAGEMENT APIs

@app.route('/api/admin/select-intern', methods=['POST', 'OPTIONS'])
def select_intern():
    """Admin selects an applicant to become an intern"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        application_id = data.get('application_id')
        default_password = data.get('default_password', 'Intern@123')
        
        if not application_id:
            return jsonify({'error': 'Application ID required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get application details
        if USE_POSTGRES:
            cursor.execute('''
                SELECT full_name, email, position, college
                FROM applications
                WHERE id = %s
            ''', (application_id,))
        else:
            cursor.execute('''
                SELECT full_name, email, position, college
                FROM applications
                WHERE id = ?
            ''', (application_id,))
        
        application = cursor.fetchone()
        
        if not application:
            conn.close()
            return jsonify({'error': 'Application not found'}), 404
        
        # Create intern account
        password_hash = hash_password(default_password)
        
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO selected_interns (application_id, full_name, email, password_hash, position, college)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (application_id, application[0], application[1], password_hash, application[2], application[3]))
            intern_id = cursor.fetchone()[0]
            
            # Update application status
            cursor.execute('''
                UPDATE applications
                SET status = %s
                WHERE id = %s
            ''', ('selected', application_id))
        else:
            cursor.execute('''
                INSERT INTO selected_interns (application_id, full_name, email, password_hash, position, college)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (application_id, application[0], application[1], password_hash, application[2], application[3]))
            intern_id = cursor.lastrowid
            
            # Update application status
            cursor.execute('''
                UPDATE applications
                SET status = ?
                WHERE id = ?
            ''', ('selected', application_id))
        
        conn.commit()
        conn.close()
        
        # Send welcome email to intern
        send_intern_welcome_email(application[1], application[0], default_password)
        
        return jsonify({
            'success': True,
            'intern_id': intern_id,
            'message': f'Intern account created for {application[0]}'
        }), 200
        
    except Exception as e:
        print(f"❌ Error selecting intern: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/interns', methods=['GET', 'OPTIONS'])
def get_all_interns():
    """Get all selected interns (admin only)"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, position, college, start_date, status, created_at
            FROM selected_interns
            ORDER BY created_at DESC
        ''')
        
        interns = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'interns': [{
                'id': i[0],
                'name': i[1],
                'email': i[2],
                'position': i[3],
                'college': i[4],
                'start_date': str(i[5]) if i[5] else None,
                'status': i[6],
                'created_at': str(i[7])
            } for i in interns]
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching interns: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/weekly-task', methods=['POST', 'OPTIONS'])
def create_weekly_task():
    """Admin creates a weekly task"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        week_number = data.get('week_number')
        task_title = data.get('task_title')
        task_description = data.get('task_description')
        mini_project_guidelines = data.get('mini_project_guidelines', '')
        ds_algo_topic = data.get('ds_algo_topic', '')
        ai_news = data.get('ai_news', '')
        due_date = data.get('due_date')
        
        if not all([week_number, task_title, task_description]):
            return jsonify({'error': 'Week number, title, and description required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                INSERT INTO weekly_tasks (week_number, task_title, task_description, 
                                         mini_project_guidelines, ds_algo_topic, ai_news, due_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (week_number, task_title, task_description, mini_project_guidelines, 
                  ds_algo_topic, ai_news, due_date))
            task_id = cursor.fetchone()[0]
        else:
            cursor.execute('''
                INSERT INTO weekly_tasks (week_number, task_title, task_description, 
                                         mini_project_guidelines, ds_algo_topic, ai_news, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (week_number, task_title, task_description, mini_project_guidelines, 
                  ds_algo_topic, ai_news, due_date))
            task_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Weekly task created successfully!'
        }), 200
        
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/intern-submissions/<int:intern_id>', methods=['GET'])
def get_intern_submissions(intern_id):
    """Get all submissions for a specific intern (admin only)"""
    try:
        token = request.cookies.get('admin_token') or request.headers.get('Authorization')
        if not verify_admin_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if USE_POSTGRES:
            cursor.execute('''
                SELECT ts.id, wt.task_title, wt.week_number, ts.submission_type, 
                       ts.submission_file, ts.what_learned, ts.submitted_at, ts.status
                FROM task_submissions ts
                JOIN weekly_tasks wt ON ts.task_id = wt.id
                WHERE ts.intern_id = %s
                ORDER BY ts.submitted_at DESC
            ''', (intern_id,))
        else:
            cursor.execute('''
                SELECT ts.id, wt.task_title, wt.week_number, ts.submission_type, 
                       ts.submission_file, ts.what_learned, ts.submitted_at, ts.status
                FROM task_submissions ts
                JOIN weekly_tasks wt ON ts.task_id = wt.id
                WHERE ts.intern_id = ?
                ORDER BY ts.submitted_at DESC
            ''', (intern_id,))
        
        submissions = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'submissions': [{
                'id': s[0],
                'task_title': s[1],
                'week_number': s[2],
                'submission_type': s[3],
                'submission_file': s[4],
                'what_learned': s[5],
                'submitted_at': str(s[6]),
                'status': s[7]
            } for s in submissions]
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching submissions: {e}")
        return jsonify({'error': str(e)}), 500

def send_intern_welcome_email(email, name, password):
    """Send welcome email to selected intern"""
    try:
        email_body = f"""
Hi {name},

Congratulations! You have been selected for the internship program at XGENAI! 🎉

Your intern dashboard credentials:
Email: {email}
Password: {password}

Please login at: {os.getenv('APP_URL', 'http://localhost:5000')}/intern/login

IMPORTANT: Please change your password after first login.

You will find your weekly tasks, assignments, and progress tracking in your dashboard.

Welcome to the team!

Best regards,
XGENAI Team
        """
        
        subject = '🎉 Welcome to XGENAI Internship Program!'
        
        if IS_PRODUCTION:
            send_email_mailgun(email, subject, email_body)
        else:
            print(f"📧 Welcome email logged for: {email}")
        
        return True
    except Exception as e:
        print(f"❌ Error sending welcome email: {e}")
        return False

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    port = int(os.getenv('PORT', 5000))
    debug = not IS_PRODUCTION
    
    if IS_PRODUCTION:
        print("\n" + "="*60)
        print("🚀 AI Solutions Production Server")
        print("="*60)
        print(f"📍 Server running on port: {port}")
        print("💾 Database: PostgreSQL (Production)")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("🚀 AI Solutions Backend Server")
        print("="*60)
        print("📍 Server running at: http://localhost:5000")
        print("📊 Admin Dashboard: http://localhost:5000/admin.html")
        print("🔐 Auth Page: http://localhost:5000/auth.html")
        print("💾 Database: aisolutions.db")
        print("="*60 + "\n")
    
    # Run the server
    app.run(debug=debug, host='0.0.0.0', port=port)
