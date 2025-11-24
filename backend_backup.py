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
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

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

# Use PostgreSQL in production
if IS_PRODUCTION and DATABASE_URL.startswith('postgres://'):
    # Render uses postgres:// but psycopg2 needs postgresql://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    import psycopg2
    USE_POSTGRES = True
else:
    USE_POSTGRES = False
    DB_NAME = DATABASE_URL

def get_db_connection():
    """Get database connection (SQLite or PostgreSQL)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    else:
        return sqlite3.connect(DB_NAME)

# Mailgun setup
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY', '')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', '')
MAILGUN_FROM_EMAIL = os.getenv('MAILGUN_FROM_EMAIL', 'noreply@yourdomain.com')

# Use PostgreSQL in production
if IS_PRODUCTION and DATABASE_URL.startswith('postgres://'):
    # Render uses postgres:// but psycopg2 needs postgresql://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    import psycopg2
    USE_POSTGRES = True
else:
    USE_POSTGRES = False
    DB_NAME = DATABASE_URL

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

# Routes

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

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
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = hash_password(data['password'])
        
        # Insert new user
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
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
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
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                      (datetime.now(), user[0]))
        
        # Create session token
        token = secrets.token_hex(32)
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
    """Get all users (admin only)"""
    try:
        conn = sqlite3.connect(DB_NAME)
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
                'created_at': row[5],
                'last_login': row[6]
            })
        
        conn.close()
        return jsonify({'users': users}), 200
        
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get all sent emails (admin only)"""
    try:
        conn = sqlite3.connect(DB_NAME)
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
    """Get statistics"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Total emails
        cursor.execute('SELECT COUNT(*) FROM emails')
        total_emails = cursor.fetchone()[0]
        
        # Users today
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
