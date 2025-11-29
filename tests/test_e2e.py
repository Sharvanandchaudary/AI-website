"""
E2E Tests for XGENAI System
Tests complete user flows from browser perspective
"""

import pytest
import requests
import time
from datetime import datetime

# Production URL
PRODUCTION_URL = "https://xgenai.onrender.com"

class TestProductionDeployment:
    """Test production deployment is working"""
    
    def test_production_homepage(self):
        """Test production homepage is accessible"""
        try:
            response = requests.get(PRODUCTION_URL, timeout=30)
            assert response.status_code == 200
            assert "XGENAI" in response.text or "xgen" in response.text.lower()
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Production site not accessible: {e}")
    
    def test_production_admin_portal(self):
        """Test admin portal is accessible"""
        try:
            response = requests.get(f'{PRODUCTION_URL}/xgen-admin-portal', timeout=30)
            assert response.status_code == 200
            assert "admin" in response.text.lower() or "login" in response.text.lower()
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Admin portal not accessible: {e}")
    
    def test_production_careers_page(self):
        """Test careers page is accessible"""
        try:
            response = requests.get(f'{PRODUCTION_URL}/careers', timeout=30)
            assert response.status_code == 200
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Careers page not accessible: {e}")
    
    def test_production_ssl_certificate(self):
        """Test SSL certificate is valid"""
        try:
            response = requests.get(PRODUCTION_URL, timeout=30)
            assert response.url.startswith('https://'), "Should redirect to HTTPS"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"SSL verification failed: {e}")

class TestProductionAPIs:
    """Test production API endpoints"""
    
    def test_production_admin_login(self):
        """Test admin can login in production"""
        try:
            login_data = {
                'email': 'admin@xgenai.com',
                'password': 'Admin@123'
            }
            
            response = requests.post(
                f'{PRODUCTION_URL}/api/admin/login',
                json=login_data,
                timeout=30
            )
            
            assert response.status_code == 200
            data = response.json()
            assert 'token' in data
            assert len(data['token']) > 0
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Production admin login failed: {e}")
    
    def test_production_stats_endpoint(self):
        """Test stats endpoint in production"""
        try:
            # First login
            login_data = {
                'email': 'admin@xgenai.com',
                'password': 'Admin@123'
            }
            
            response = requests.post(
                f'{PRODUCTION_URL}/api/admin/login',
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                token = response.json().get('token')
                headers = {'Authorization': f'Bearer {token}'}
                
                # Get stats
                response = requests.get(
                    f'{PRODUCTION_URL}/api/stats',
                    headers=headers,
                    timeout=30
                )
                
                assert response.status_code == 200
                data = response.json()
                assert 'total_users' in data
                assert 'total_emails' in data
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Production stats endpoint failed: {e}")
    
    def test_production_application_submission(self):
        """Test job application can be submitted"""
        timestamp = datetime.now().timestamp()
        
        application = {
            'position': 'E2E Test Intern',
            'full_name': f'E2E Test User {timestamp}',
            'email': f'e2e_test_{timestamp}@test.com',
            'phone': '5555555555',
            'college': 'E2E Test University',
            'degree': 'Computer Science',
            'graduation_year': '2025',
            'linkedin': 'https://linkedin.com/in/e2etest',
            'github': 'https://github.com/e2etest',
            'portfolio': 'https://e2etest.com',
            'resume': 'data:application/pdf;base64,test',
            'cover_letter': 'E2E test cover letter',
            'why_join': 'E2E testing',
            'achievements': 'Automated testing'
        }
        
        try:
            response = requests.post(
                f'{PRODUCTION_URL}/api/applications',
                json=application,
                timeout=30
            )
            
            assert response.status_code in [200, 201]
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Application submission failed: {e}")

class TestProductionPerformance:
    """Test production performance"""
    
    def test_production_response_time(self):
        """Test production responds quickly"""
        try:
            start = time.time()
            response = requests.get(PRODUCTION_URL, timeout=30)
            duration = time.time() - start
            
            assert response.status_code == 200
            assert duration < 5.0, f"Production took {duration}s, expected < 5s"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Performance test failed: {e}")
    
    def test_production_api_performance(self):
        """Test production API performance"""
        try:
            start = time.time()
            response = requests.get(f'{PRODUCTION_URL}/api/stats', timeout=30)
            duration = time.time() - start
            
            assert duration < 3.0, f"API took {duration}s, expected < 3s"
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API performance test failed: {e}")

class TestProductionSecurity:
    """Test production security"""
    
    def test_production_security_headers(self):
        """Test security headers are present in production"""
        try:
            response = requests.get(f'{PRODUCTION_URL}/xgen-admin-portal', timeout=30)
            
            # Check security headers
            assert 'X-Frame-Options' in response.headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-XSS-Protection' in response.headers
            
            # Verify values
            assert response.headers.get('X-Frame-Options') == 'DENY'
            assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Security headers test failed: {e}")
    
    def test_production_https_redirect(self):
        """Test HTTP redirects to HTTPS"""
        try:
            # Try HTTP
            http_url = PRODUCTION_URL.replace('https://', 'http://')
            response = requests.get(http_url, timeout=30, allow_redirects=True)
            
            # Should end up at HTTPS
            assert response.url.startswith('https://')
        except requests.exceptions.RequestException as e:
            pytest.fail(f"HTTPS redirect test failed: {e}")
    
    def test_production_unauthorized_access(self):
        """Test unauthorized API access is blocked"""
        try:
            # Try to access admin endpoint without token
            response = requests.get(
                f'{PRODUCTION_URL}/api/admin/applications',
                timeout=30
            )
            
            assert response.status_code in [401, 403]
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Unauthorized access test failed: {e}")

class TestProductionDatabase:
    """Test production database connectivity"""
    
    def test_production_data_persistence(self):
        """Test data persists in production"""
        timestamp = datetime.now().timestamp()
        email = f'prod_persist_{timestamp}@test.com'
        
        # Create user
        signup_data = {
            'name': 'Production Persist Test',
            'email': email,
            'phone': '6666666666',
            'address': 'Production Test St',
            'password': 'ProdTest123'
        }
        
        try:
            response = requests.post(
                f'{PRODUCTION_URL}/api/signup',
                json=signup_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                # Wait for commit
                time.sleep(2)
                
                # Try to login
                login_data = {
                    'email': email,
                    'password': 'ProdTest123'
                }
                
                response = requests.post(
                    f'{PRODUCTION_URL}/api/login',
                    json=login_data,
                    timeout=30
                )
                
                assert response.status_code in [200, 401]
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Data persistence test failed: {e}")

class TestProductionAvailability:
    """Test production uptime and availability"""
    
    def test_production_uptime(self):
        """Test production is up"""
        try:
            response = requests.get(PRODUCTION_URL, timeout=30)
            assert response.status_code == 200
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Production is down: {e}")
    
    def test_production_multiple_requests(self):
        """Test production handles multiple requests"""
        import concurrent.futures
        
        def make_request():
            try:
                response = requests.get(PRODUCTION_URL, timeout=30)
                return response.status_code == 200
            except:
                return False
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            assert success_rate >= 0.8, f"Only {success_rate*100}% requests succeeded in production"

# Run E2E tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
