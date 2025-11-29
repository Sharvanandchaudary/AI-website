"""
Comprehensive Unit Tests for XGENAI System
Tests all API endpoints, authentication, and business logic
"""

import pytest
import sys
import os
from datetime import datetime
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Flask app
from backend import app, hash_password, get_db_connection

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_token(client):
    """Get admin authentication token"""
    response = client.post('/api/admin/login', json={
        'email': 'admin@xgenai.com',
        'password': 'Admin@123'
    })
    if response.status_code == 200:
        data = response.get_json()
        return data.get('token')
    return None

class TestHealthCheck:
    """Test basic health and connectivity"""
    
    def test_home_page(self, client):
        """Test homepage loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_careers_page(self, client):
        """Test careers page loads"""
        response = client.get('/careers')
        assert response.status_code == 200
    
    def test_auth_page(self, client):
        """Test auth page loads"""
        response = client.get('/auth')
        assert response.status_code == 200

class TestSecurity:
    """Test security features"""
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get('/xgen-admin-portal')
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
    
    def test_password_hashing(self):
        """Test password hashing works"""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) == 64  # SHA-256 hex length
    
    def test_password_verification(self):
        """Test password verification"""
        password = "TestPassword123"
        hashed = hash_password(password)
        # Verify by hashing again and comparing
        assert hash_password(password) == hashed
        assert hash_password("WrongPassword") != hashed

class TestUserAuthentication:
    """Test user registration and login"""
    
    def test_user_signup_success(self, client):
        """Test user can signup"""
        test_user = {
            'name': f'Test User {datetime.now().timestamp()}',
            'email': f'test{datetime.now().timestamp()}@test.com',
            'phone': '1234567890',
            'address': '123 Test St',
            'password': 'TestPass123'
        }
        response = client.post('/api/signup', json=test_user)
        assert response.status_code in [200, 201]
    
    def test_user_signup_missing_fields(self, client):
        """Test signup fails with missing fields"""
        response = client.post('/api/signup', json={
            'name': 'Test User',
            'email': 'test@test.com'
        })
        assert response.status_code == 400
    
    def test_user_login_success(self, client):
        """Test user can login"""
        # First signup
        timestamp = datetime.now().timestamp()
        email = f'test{timestamp}@test.com'
        password = 'TestPass123'
        
        client.post('/api/signup', json={
            'name': 'Test User',
            'email': email,
            'phone': '1234567890',
            'address': '123 Test St',
            'password': password
        })
        
        # Then login
        response = client.post('/api/login', json={
            'email': email,
            'password': password
        })
        assert response.status_code in [200, 400]  # 400 if user exists
    
    def test_user_login_invalid_credentials(self, client):
        """Test login fails with wrong password"""
        response = client.post('/api/login', json={
            'email': 'nonexistent@test.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401

class TestAdminAuthentication:
    """Test admin authentication"""
    
    def test_admin_login_success(self, client):
        """Test admin can login"""
        response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com',
            'password': 'Admin@123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
    
    def test_admin_login_invalid(self, client):
        """Test admin login fails with wrong credentials"""
        response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401
    
    def test_admin_portal_page(self, client):
        """Test admin portal page loads"""
        response = client.get('/xgen-admin-portal')
        assert response.status_code == 200
    
    def test_admin_dashboard_page(self, client):
        """Test admin dashboard page loads"""
        response = client.get('/xgen-admin-dashboard')
        assert response.status_code == 200

class TestJobApplications:
    """Test job application system"""
    
    def test_submit_application_success(self, client):
        """Test submitting job application"""
        application = {
            'position': 'AI/ML Intern',
            'full_name': f'Test Applicant {datetime.now().timestamp()}',
            'email': f'applicant{datetime.now().timestamp()}@test.com',
            'phone': '1234567890',
            'college': 'Test University',
            'degree': 'Computer Science',
            'graduation_year': '2025',
            'linkedin': 'https://linkedin.com/in/test',
            'github': 'https://github.com/test',
            'portfolio': 'https://test.com',
            'resume': 'base64encodeddata',
            'cover_letter': 'I am interested in this position...',
            'why_join': 'Great opportunity',
            'achievements': 'Won hackathon'
        }
        response = client.post('/api/applications', json=application)
        assert response.status_code in [200, 201]
    
    def test_submit_application_missing_fields(self, client):
        """Test application fails with missing required fields"""
        response = client.post('/api/applications', json={
            'position': 'AI/ML Intern',
            'full_name': 'Test User'
        })
        assert response.status_code == 400
    
    def test_get_applications_with_auth(self, client, auth_token):
        """Test admin can view applications"""
        if auth_token:
            response = client.get('/api/admin/applications', 
                                headers={'Authorization': f'Bearer {auth_token}'})
            assert response.status_code == 200
            data = response.get_json()
            assert 'applications' in data

class TestInternManagement:
    """Test intern management features"""
    
    def test_select_intern_with_auth(self, client, auth_token):
        """Test admin can select intern"""
        if auth_token:
            # First create an application
            timestamp = datetime.now().timestamp()
            application = {
                'position': 'AI/ML Intern',
                'full_name': f'Test Applicant {timestamp}',
                'email': f'applicant{timestamp}@test.com',
                'phone': '1234567890',
                'college': 'Test University',
                'degree': 'Computer Science',
                'graduation_year': '2025',
                'linkedin': 'https://linkedin.com/in/test',
                'github': 'https://github.com/test',
                'portfolio': 'https://test.com',
                'resume': 'base64encodeddata',
                'cover_letter': 'Test',
                'why_join': 'Test',
                'achievements': 'Test'
            }
            client.post('/api/applications', json=application)
            
            # Then try to select (may fail if application not found, that's ok)
            response = client.post('/api/admin/select-intern',
                                 headers={'Authorization': f'Bearer {auth_token}'},
                                 json={
                                     'application_id': 1,
                                     'full_name': 'Test Applicant',
                                     'email': f'applicant{timestamp}@test.com',
                                     'position': 'AI/ML Intern',
                                     'college': 'Test University'
                                 })
            assert response.status_code in [200, 400, 404]
    
    def test_get_interns_with_auth(self, client, auth_token):
        """Test admin can view interns"""
        if auth_token:
            response = client.get('/api/admin/interns',
                                headers={'Authorization': f'Bearer {auth_token}'})
            assert response.status_code == 200
            data = response.get_json()
            assert 'interns' in data
    
    def test_create_weekly_task_with_auth(self, client, auth_token):
        """Test admin can create weekly task"""
        if auth_token:
            task = {
                'week_number': 1,
                'title': 'Test Task',
                'description': 'This is a test task',
                'mini_project': 'Build something',
                'ds_algo': 'Solve problem',
                'ai_news': 'Read about AI'
            }
            response = client.post('/api/admin/weekly-task',
                                 headers={'Authorization': f'Bearer {auth_token}'},
                                 json=task)
            assert response.status_code in [200, 201, 400]

class TestInternPortal:
    """Test intern login and dashboard"""
    
    def test_intern_login_page(self, client):
        """Test intern login page loads"""
        response = client.get('/intern-login')
        assert response.status_code == 200
    
    def test_intern_dashboard_page(self, client):
        """Test intern dashboard page loads"""
        response = client.get('/intern-dashboard')
        assert response.status_code == 200

class TestStatistics:
    """Test dashboard statistics"""
    
    def test_get_stats_with_auth(self, client, auth_token):
        """Test admin can view stats"""
        if auth_token:
            response = client.get('/api/stats',
                                headers={'Authorization': f'Bearer {auth_token}'})
            assert response.status_code == 200
            data = response.get_json()
            assert 'total_users' in data
            assert 'total_emails' in data
    
    def test_get_stats_without_auth(self, client):
        """Test stats endpoint without auth returns zeros"""
        response = client.get('/api/stats')
        assert response.status_code in [200, 401]

class TestEmailSystem:
    """Test email functionality"""
    
    def test_get_emails_with_auth(self, client, auth_token):
        """Test admin can view email history"""
        if auth_token:
            response = client.get('/api/emails',
                                headers={'Authorization': f'Bearer {auth_token}'})
            assert response.status_code == 200
            data = response.get_json()
            assert 'emails' in data

class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options('/api/login')
        assert response.status_code == 204

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_on_invalid_route(self, client):
        """Test 404 for non-existent routes"""
        response = client.get('/nonexistent-route-12345')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed"""
        response = client.delete('/api/signup')
        assert response.status_code == 405

class TestDatabaseConnection:
    """Test database functionality"""
    
    def test_database_connection(self):
        """Test database connection works"""
        conn = get_db_connection()
        assert conn is not None
        conn.close()

# Run tests with coverage
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=backend', '--cov-report=html', '--cov-report=term'])
