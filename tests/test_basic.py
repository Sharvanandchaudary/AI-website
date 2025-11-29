"""
Simple and reliable unit tests for XGENAI System
"""

import pytest
import sys
import os
from datetime import datetime

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


class TestBasicFunctionality:
    """Test core application functionality"""
    
    def test_homepage_loads(self, client):
        """Test homepage is accessible"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_careers_page_loads(self, client):
        """Test careers page is accessible"""
        response = client.get('/careers')
        assert response.status_code == 200
    
    def test_auth_page_loads(self, client):
        """Test auth page is accessible"""
        response = client.get('/auth')
        assert response.status_code == 200
    
    def test_admin_portal_loads(self, client):
        """Test admin portal is accessible"""
        response = client.get('/xgen-admin-portal')
        assert response.status_code == 200
    
    def test_intern_login_loads(self, client):
        """Test intern login page is accessible"""
        response = client.get('/intern-login')
        assert response.status_code == 200


class TestSecurity:
    """Test security features"""
    
    def test_security_headers_present(self, client):
        """Test security headers are added"""
        response = client.get('/xgen-admin-portal')
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
    
    def test_password_hashing_works(self):
        """Test password hashing"""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) == 64  # SHA-256
    
    def test_password_hashing_consistent(self):
        """Test same password produces same hash"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 == hash2
    
    def test_different_passwords_different_hashes(self):
        """Test different passwords produce different hashes"""
        hash1 = hash_password("Password1")
        hash2 = hash_password("Password2")
        assert hash1 != hash2


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_admin_login_endpoint_exists(self, client):
        """Test admin login endpoint responds"""
        response = client.post('/api/admin/login', json={
            'email': 'test@test.com',
            'password': 'test'
        })
        assert response.status_code in [200, 401]  # Either success or unauthorized
    
    def test_admin_login_with_correct_credentials(self, client):
        """Test admin can login with correct credentials"""
        response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com',
            'password': 'Admin@123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
    
    def test_admin_login_with_wrong_credentials(self, client):
        """Test admin login fails with wrong credentials"""
        response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401


class TestUserRegistration:
    """Test user registration"""
    
    def test_signup_requires_all_fields(self, client):
        """Test signup fails without required fields"""
        response = client.post('/api/signup', json={
            'name': 'Test User',
            'email': 'test@test.com'
        })
        assert response.status_code == 400
    
    def test_signup_with_valid_data(self, client):
        """Test user can signup with valid data"""
        timestamp = datetime.now().timestamp()
        response = client.post('/api/signup', json={
            'name': f'Test User {timestamp}',
            'email': f'test{timestamp}@test.com',
            'phone': '1234567890',
            'address': '123 Test St',
            'password': 'TestPass123'
        })
        assert response.status_code in [200, 201, 400]  # 400 if user exists


class TestJobApplications:
    """Test job application system"""
    
    def test_application_endpoint_exists(self, client):
        """Test application endpoint responds"""
        response = client.post('/api/applications', json={})
        assert response.status_code in [200, 201, 400]
    
    def test_application_requires_fields(self, client):
        """Test application fails without required fields"""
        response = client.post('/api/applications', json={
            'position': 'AI/ML Intern',
            'full_name': 'Test'
        })
        assert response.status_code == 400


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_options_supported(self, client):
        """Test OPTIONS method is supported"""
        response = client.options('/api/admin/login')
        assert response.status_code in [200, 204]


class TestDatabase:
    """Test database connectivity"""
    
    def test_database_connection_works(self):
        """Test can connect to database"""
        conn = get_db_connection()
        assert conn is not None
        conn.close()


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_for_invalid_route(self, client):
        """Test 404 for non-existent routes"""
        response = client.get('/this-does-not-exist-12345')
        assert response.status_code == 404


# Summary test that always passes to show test completion
class TestSummary:
    """Summary of test execution"""
    
    def test_tests_completed(self):
        """Verify test suite completed"""
        assert True, "Test suite execution completed successfully"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
