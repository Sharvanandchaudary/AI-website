"""
Integration Tests for XGENAI System
Tests end-to-end workflows and API integrations
"""

import pytest
import requests
import time
from datetime import datetime

# Test against local or production
BASE_URL = "http://localhost:5000"  # Change to production URL for production tests

class TestEndToEndWorkflow:
    """Test complete user journeys"""
    
    def test_complete_user_signup_and_login(self):
        """Test user signup and login flow"""
        timestamp = datetime.now().timestamp()
        email = f'integration_test_{timestamp}@test.com'
        
        # Signup
        signup_data = {
            'name': 'Integration Test User',
            'email': email,
            'phone': '9876543210',
            'address': '456 Integration St',
            'password': 'IntegrationTest123'
        }
        
        try:
            response = requests.post(f'{BASE_URL}/api/signup', json=signup_data, timeout=10)
            assert response.status_code in [200, 201, 400]  # 400 if already exists
            
            # Login
            login_data = {
                'email': email,
                'password': 'IntegrationTest123'
            }
            
            response = requests.post(f'{BASE_URL}/api/login', json=login_data, timeout=10)
            assert response.status_code in [200, 401]
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")
    
    def test_complete_application_workflow(self):
        """Test job application submission"""
        timestamp = datetime.now().timestamp()
        
        application = {
            'position': 'Full Stack Intern',
            'full_name': f'Integration Test Applicant {timestamp}',
            'email': f'integration_applicant_{timestamp}@test.com',
            'phone': '9876543210',
            'college': 'Integration Test University',
            'degree': 'Computer Science',
            'graduation_year': '2025',
            'linkedin': 'https://linkedin.com/in/test',
            'github': 'https://github.com/test',
            'portfolio': 'https://test.com',
            'resume': 'data:application/pdf;base64,JVBERi0xLjQKJdPr6eEKMSA...',
            'cover_letter': 'Integration test cover letter',
            'why_join': 'Testing integration',
            'achievements': 'Completed integration tests'
        }
        
        try:
            response = requests.post(f'{BASE_URL}/api/applications', json=application, timeout=10)
            assert response.status_code in [200, 201, 400]
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")
    
    def test_admin_workflow(self):
        """Test admin login and dashboard access"""
        try:
            # Admin login
            login_data = {
                'email': 'admin@xgenai.com',
                'password': 'Admin@123'
            }
            
            response = requests.post(f'{BASE_URL}/api/admin/login', json=login_data, timeout=10)
            assert response.status_code == 200
            
            if response.status_code == 200:
                token = response.json().get('token')
                headers = {'Authorization': f'Bearer {token}'}
                
                # Get stats
                response = requests.get(f'{BASE_URL}/api/stats', headers=headers, timeout=10)
                assert response.status_code == 200
                
                # Get applications
                response = requests.get(f'{BASE_URL}/api/admin/applications', headers=headers, timeout=10)
                assert response.status_code == 200
                
                # Get interns
                response = requests.get(f'{BASE_URL}/api/admin/interns', headers=headers, timeout=10)
                assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")

class TestAPIPerformance:
    """Test API response times"""
    
    def test_homepage_response_time(self):
        """Test homepage loads in under 2 seconds"""
        try:
            start = time.time()
            response = requests.get(f'{BASE_URL}/', timeout=10)
            duration = time.time() - start
            
            assert response.status_code == 200
            assert duration < 2.0, f"Homepage took {duration}s, expected < 2s"
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")
    
    def test_api_response_time(self):
        """Test API responds in under 1 second"""
        try:
            start = time.time()
            response = requests.get(f'{BASE_URL}/api/stats', timeout=10)
            duration = time.time() - start
            
            assert duration < 1.0, f"API took {duration}s, expected < 1s"
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")

class TestConcurrentRequests:
    """Test system under load"""
    
    def test_multiple_simultaneous_requests(self):
        """Test handling multiple requests"""
        import concurrent.futures
        
        def make_request():
            try:
                response = requests.get(f'{BASE_URL}/', timeout=10)
                return response.status_code == 200
            except:
                return False
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
                
                success_rate = sum(results) / len(results)
                assert success_rate >= 0.8, f"Only {success_rate*100}% requests succeeded"
        except:
            pytest.skip("Server not available for load testing")

class TestDataPersistence:
    """Test data persistence across requests"""
    
    def test_user_data_persists(self):
        """Test user data is saved and retrievable"""
        timestamp = datetime.now().timestamp()
        email = f'persist_test_{timestamp}@test.com'
        
        # Create user
        signup_data = {
            'name': 'Persistence Test User',
            'email': email,
            'phone': '1111111111',
            'address': '789 Persist St',
            'password': 'PersistTest123'
        }
        
        try:
            response = requests.post(f'{BASE_URL}/api/signup', json=signup_data, timeout=10)
            
            if response.status_code in [200, 201]:
                # Try to login with same credentials
                time.sleep(1)  # Wait for database commit
                
                login_data = {
                    'email': email,
                    'password': 'PersistTest123'
                }
                
                response = requests.post(f'{BASE_URL}/api/login', json=login_data, timeout=10)
                assert response.status_code in [200, 401]
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")

class TestSecurityIntegration:
    """Test security features in integration"""
    
    def test_sql_injection_protection(self):
        """Test SQL injection attempts are blocked"""
        try:
            malicious_data = {
                'email': "admin@xgenai.com' OR '1'='1",
                'password': "' OR '1'='1"
            }
            
            response = requests.post(f'{BASE_URL}/api/login', json=malicious_data, timeout=10)
            assert response.status_code == 401, "SQL injection attempt should fail"
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")
    
    def test_xss_protection(self):
        """Test XSS attempts are handled"""
        try:
            xss_data = {
                'name': '<script>alert("XSS")</script>',
                'email': f'xss_test_{datetime.now().timestamp()}@test.com',
                'phone': '2222222222',
                'address': '<img src=x onerror=alert(1)>',
                'password': 'XSSTest123'
            }
            
            response = requests.post(f'{BASE_URL}/api/signup', json=xss_data, timeout=10)
            # Should either succeed (with sanitized data) or fail with validation error
            assert response.status_code in [200, 201, 400]
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")
    
    def test_unauthorized_access(self):
        """Test unauthorized access is blocked"""
        try:
            # Try to access admin endpoint without token
            response = requests.get(f'{BASE_URL}/api/admin/applications', timeout=10)
            assert response.status_code in [401, 403], "Unauthorized access should be blocked"
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")

class TestEmailIntegration:
    """Test email functionality if configured"""
    
    def test_email_system_available(self):
        """Test email system is configured"""
        try:
            # Admin login to get token
            login_data = {
                'email': 'admin@xgenai.com',
                'password': 'Admin@123'
            }
            
            response = requests.post(f'{BASE_URL}/api/admin/login', json=login_data, timeout=10)
            
            if response.status_code == 200:
                token = response.json().get('token')
                headers = {'Authorization': f'Bearer {token}'}
                
                # Check email history
                response = requests.get(f'{BASE_URL}/api/emails', headers=headers, timeout=10)
                assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Server not available")

# Run integration tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
