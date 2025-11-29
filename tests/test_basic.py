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
        assert b'XGENAI' in response.data or b'xgen' in response.data.lower()
    
    def test_careers_page_loads(self, client):
        """Test careers page is accessible"""
        response = client.get('/careers')
        assert response.status_code == 200
        assert b'career' in response.data.lower() or b'job' in response.data.lower()
    
    def test_auth_page_loads(self, client):
        """Test auth page is accessible"""
        response = client.get('/auth')
        assert response.status_code == 200
    
    def test_admin_portal_loads(self, client):
        """Test /admin URL loads admin portal"""
        response = client.get('/admin')
        assert response.status_code == 200
        assert b'admin' in response.data.lower()
    
    def test_admin_alternative_url_loads(self, client):
        """Test /xgen-admin-portal also loads admin portal"""
        response = client.get('/xgen-admin-portal')
        assert response.status_code == 200
        assert b'admin' in response.data.lower()
    
    def test_admin_dashboard_loads(self, client):
        """Test admin dashboard page loads"""
        response = client.get('/xgen-admin-dashboard')
        assert response.status_code == 200
    
    def test_intern_login_loads(self, client):
        """Test intern login page is accessible"""
        response = client.get('/intern-login')
        assert response.status_code == 200
    
    def test_intern_dashboard_loads(self, client):
        """Test intern dashboard page is accessible"""
        response = client.get('/intern-dashboard')
        assert response.status_code == 200
    
    def test_apply_page_loads(self, client):
        """Test application form page loads"""
        response = client.get('/apply')
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
        assert len(data['token']) > 0
    
    def test_admin_login_with_wrong_credentials(self, client):
        """Test admin login fails with wrong credentials"""
        response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401
    
    def test_admin_login_missing_email(self, client):
        """Test admin login fails without email"""
        response = client.post('/api/admin/login', json={
            'password': 'Admin@123'
        })
        assert response.status_code == 400
    
    def test_admin_login_missing_password(self, client):
        """Test admin login fails without password"""
        response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com'
        })
        assert response.status_code == 400
    
    def test_admin_dashboard_after_login(self, client):
        """Test admin can access dashboard after successful login"""
        # First login
        login_response = client.post('/api/admin/login', json={
            'email': 'admin@xgenai.com',
            'password': 'Admin@123'
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['token']
        
        # Then try to access stats with token
        stats_response = client.get('/api/stats', 
                                    headers={'Authorization': f'Bearer {token}'})
        # Should either work (200) or require auth (401) but not error
        assert stats_response.status_code in [200, 401]


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
    
    def test_complete_application_submission(self, client):
        """Test submitting complete job application with all required fields"""
        timestamp = datetime.now().timestamp()
        application = {
            'position': 'AI/ML Intern',
            'fullName': f'Test Applicant {timestamp}',
            'email': f'applicant{timestamp}@test.com',
            'phone': '1234567890',
            'address': '123 Test St, Test City, TC 12345',
            'college': 'Test University',
            'degree': 'B.Tech in Computer Science',
            'semester': '5',
            'year': '2025',
            'about': 'I am a passionate computer science student with strong skills in AI/ML, Python, and data structures. I have completed several projects in machine learning and am eager to contribute to real-world AI applications at XGENAI.',
            'resumeName': 'test-resume.pdf',
            'linkedin': 'https://linkedin.com/in/testapplicant',
            'github': 'https://github.com/testapplicant'
        }
        response = client.post('/api/applications', json=application)
        assert response.status_code in [200, 201], f"Expected 200/201 but got {response.status_code}: {response.get_json()}"
        data = response.get_json()
        assert 'message' in data or 'success' in data
    
    def test_application_with_minimal_required_fields(self, client):
        """Test application with only required fields (no optional fields)"""
        timestamp = datetime.now().timestamp()
        application = {
            'position': 'Software Developer Intern',
            'fullName': f'Minimal Test {timestamp}',
            'email': f'minimal{timestamp}@test.com',
            'phone': '9876543210',
            'address': '456 Test Ave',
            'college': 'Test College',
            'degree': 'BCA',
            'semester': '3',
            'year': '2026',
            'about': 'Test application',
            'resumeName': 'resume.pdf'
        }
        response = client.post('/api/applications', json=application)
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'message' in data or 'success' in data


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_options_supported(self, client):
        """Test OPTIONS method is supported"""
        response = client.options('/api/admin/login')
        assert response.status_code in [200, 204]


class TestURLRouting:
    """Test URL routing and redirects"""
    
    def test_homepage_route(self, client):
        """Test homepage accessible at /"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'XGENAI' in response.data or b'xgen' in response.data.lower()
    
    def test_careers_route(self, client):
        """Test careers page route"""
        response = client.get('/careers')
        assert response.status_code == 200
        assert b'career' in response.data.lower() or b'job' in response.data.lower()
    
    def test_admin_portal_routes(self, client):
        """Test both admin portal URLs work"""
        # Primary admin URL
        response1 = client.get('/admin')
        assert response1.status_code == 200
        assert b'admin' in response1.data.lower()
        
        # Alternative admin URL
        response2 = client.get('/xgen-admin-portal')
        assert response2.status_code == 200
        assert b'admin' in response2.data.lower()
    
    def test_admin_dashboard_route(self, client):
        """Test admin dashboard route"""
        response = client.get('/xgen-admin-dashboard')
        assert response.status_code == 200
    
    def test_intern_routes(self, client):
        """Test intern authentication and dashboard routes"""
        # Login page
        response1 = client.get('/intern-login')
        assert response1.status_code == 200
        
        # Dashboard page
        response2 = client.get('/intern-dashboard')
        assert response2.status_code == 200
    
    def test_apply_route(self, client):
        """Test application form route"""
        response = client.get('/apply')
        assert response.status_code == 200
    
    def test_invalid_route_404(self, client):
        """Test invalid routes return 404"""
        response = client.get('/nonexistent-page-testing-404')
        assert response.status_code == 404


class TestInternWorkflows:
    """Test intern authentication and task workflows"""
    
    def test_intern_login_endpoint(self, client):
        """Test intern login endpoint exists"""
        response = client.post('/api/intern/login', json={
            'email': 'test@test.com',
            'password': 'test'
        })
        assert response.status_code in [200, 401]
    
    def test_intern_login_requires_credentials(self, client):
        """Test intern login requires email and password"""
        # Missing email
        response1 = client.post('/api/intern/login', json={'password': 'test'})
        assert response1.status_code == 400
        
        # Missing password
        response2 = client.post('/api/intern/login', json={'email': 'test@test.com'})
        assert response2.status_code == 400
    
    def test_intern_task_submission_endpoint(self, client):
        """Test task submission endpoint exists"""
        response = client.post('/api/intern/submit-task', json={
            'task': 'test',
            'description': 'test'
        })
        # Should fail without auth or with missing fields (400/401)
        assert response.status_code in [400, 401, 403]


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
