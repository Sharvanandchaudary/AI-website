# Flask Backend for AI Solutions Website
# This server handles user authentication and email notifications

from flask import Flask, request, jsonify, send_from_directory
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

# Use PostgreSQL in production - Check for postgres:// or postgresql:// URL
if DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://'):
    # Render uses postgres:// but psycopg2 needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    import psycopg2
    USE_POSTGRES = True
    print(f"🔧 Using PostgreSQL database")
else:
    USE_POSTGRES = False
    DB_NAME = DATABASE_URL
    print(f"🔧 Using SQLite database: {DB_NAME}")

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

# Routes

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/careers')
def careers_page():
    """Serve careers page"""
    return send_from_directory('.', 'careers.html')

@app.route('/auth')
def auth_page():
    """Serve authentication page"""
    return send_from_directory('.', 'auth.html')

@app.route('/dashboard')
def dashboard_page():
    """Serve user dashboard page"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/apply')
def apply_page():
    """Serve application form page"""
    return send_from_directory('pages', 'apply.html')

@app.route('/admin/login')
def admin_login_page():
    """Serve admin login page"""
    return send_from_directory('.', 'admin-login.html')

@app.route('/admin')
def admin_page():
    """Serve admin dashboard (requires authentication)"""
    # Check for admin token in cookie/header
    token = request.cookies.get('admin_token') or request.headers.get('Authorization')
    if not verify_admin_token(token):
        return send_from_directory('.', 'admin-login.html')
    return send_from_directory('.', 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

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
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Total emails
        cursor.execute('SELECT COUNT(*) FROM emails')
        total_emails = cursor.fetchone()[0]
        
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
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_emails': total_emails,
            'today_users': today_users
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

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

@app.route('/api/applications', methods=['POST'])
def submit_application():
    """Submit job application"""
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

@app.route('/api/admin/applications', methods=['GET'])
def get_all_applications():
    """Get all job applications (admin only - requires authentication)"""
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
