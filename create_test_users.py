"""
Helper script to create test users for the ZGENAI portal
Run this to set up demo intern and recruiter accounts
"""

import psycopg2
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """Create test intern and recruiter accounts"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Create test intern
    intern_email = "intern@zgenai.com"
    intern_password = "Intern@123"
    intern_hash = hash_password(intern_password)
    
    try:
        cursor.execute('''
            INSERT INTO selected_interns (full_name, email, password_hash, position, college, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', ("Test Intern", intern_email, intern_hash, "Software Developer Intern", "Demo College", "active"))
        print(f"✅ Created intern account: {intern_email} / {intern_password}")
    except Exception as e:
        print(f"⚠️ Intern account may already exist: {e}")
    
    # Create test recruiter
    recruiter_email = "recruiter@zgenai.com"
    recruiter_password = "Recruiter@123"
    recruiter_hash = hash_password(recruiter_password)
    
    try:
        cursor.execute('''
            INSERT INTO recruiters (full_name, email, password_hash, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        ''', ("Test Recruiter", recruiter_email, recruiter_hash, "active"))
        print(f"✅ Created recruiter account: {recruiter_email} / {recruiter_password}")
    except Exception as e:
        print(f"⚠️ Recruiter account may already exist: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 Test accounts created successfully!")
    print("="*60)
    print(f"Intern Login:     {intern_email} / {intern_password}")
    print(f"Recruiter Login:  {recruiter_email} / {recruiter_password}")
    print("="*60)

if __name__ == "__main__":
    create_test_users()
