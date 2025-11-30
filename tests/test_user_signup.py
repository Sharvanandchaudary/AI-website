"""
Comprehensive test suite for user signup and dashboard display functionality
Tests user registration, authentication, and admin dashboard data display
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from datetime import datetime
from backend import app, get_db_connection, hash_password, USE_POSTGRES

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def admin_token(client):
    """Get admin authentication token"""
    response = client.post('/api/admin/login',
        json={'email': 'admin@xgenai.com', 'password': 'Admin@123'},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    return data['token']

@pytest.fixture
def clean_test_user():
    """Clean up test user before and after tests"""
    test_email = 'testuser@example.com'
    
    # Cleanup before test
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if USE_POSTGRES:
            cursor.execute('DELETE FROM users WHERE email = %s', (test_email,))
        else:
            cursor.execute('DELETE FROM users WHERE email = ?', (test_email,))
        conn.commit()
    except:
        pass
    finally:
        conn.close()
    
    yield test_email
    
    # Cleanup after test
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if USE_POSTGRES:
            cursor.execute('DELETE FROM users WHERE email = %s', (test_email,))
        else:
            cursor.execute('DELETE FROM users WHERE email = ?', (test_email,))
        conn.commit()
    except:
        pass
    finally:
        conn.close()


class TestUserSignup:
    """Test user signup functionality"""
    
    def test_signup_success(self, client, clean_test_user):
        """Test successful user registration"""
        response = client.post('/api/signup',
            json={
                'name': 'Test User',
                'email': clean_test_user,
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Account created successfully!'
        assert 'user_id' in data
        assert data['email'] == clean_test_user
    
    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields"""
        # Missing name
        response = client.post('/api/signup',
            json={
                'email': 'test@example.com',
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'name' in data['error'].lower()
        
        # Missing email
        response = client.post('/api/signup',
            json={
                'name': 'Test User',
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Missing password
        response = client.post('/api/signup',
            json={
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'address': '123 Test Street'
            },
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_signup_duplicate_email(self, client, clean_test_user):
        """Test signup with already registered email"""
        # First signup
        response = client.post('/api/signup',
            json={
                'name': 'Test User',
                'email': clean_test_user,
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Duplicate signup
        response = client.post('/api/signup',
            json={
                'name': 'Test User 2',
                'email': clean_test_user,
                'phone': '0987654321',
                'address': '456 Test Avenue',
                'password': 'testpass456'
            },
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'already exists' in data['error'].lower()
    
    def test_password_hashing(self, client, clean_test_user):
        """Test that passwords are properly hashed in database"""
        password = 'testpass123'
        
        # Create user
        response = client.post('/api/signup',
            json={
                'name': 'Test User',
                'email': clean_test_user,
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': password
            },
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Check database
        conn = get_db_connection()
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute('SELECT password_hash FROM users WHERE email = %s', (clean_test_user,))
        else:
            cursor.execute('SELECT password_hash FROM users WHERE email = ?', (clean_test_user,))
        
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        password_hash = result[0]
        assert password_hash != password  # Password should be hashed
        assert len(password_hash) == 64  # SHA256 hash length
        # Verify it's a valid hex string
        try:
            int(password_hash, 16)
        except ValueError:
            pytest.fail("Password hash is not a valid hexadecimal string")


class TestUserDashboardDisplay:
    """Test user display in admin dashboard"""
    
    def test_get_users_unauthorized(self, client):
        """Test getting users without authentication"""
        response = client.get('/api/users')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'unauthorized' in data['error'].lower()
    
    def test_get_users_success(self, client, admin_token, clean_test_user):
        """Test getting users list with admin authentication"""
        # Create a test user first
        client.post('/api/signup',
            json={
                'name': 'Test User',
                'email': clean_test_user,
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        
        # Get users list
        response = client.get('/api/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert isinstance(data['users'], list)
        assert len(data['users']) > 0
        
        # Check user data structure
        user = data['users'][0]
        assert 'id' in user
        assert 'name' in user
        assert 'email' in user
        assert 'phone' in user
        assert 'created_at' in user
    
    def test_stats_include_users(self, client, admin_token, clean_test_user):
        """Test that stats endpoint includes user count"""
        # Create a test user
        client.post('/api/signup',
            json={
                'name': 'Test User',
                'email': clean_test_user,
                'phone': '1234567890',
                'address': '123 Test Street',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        
        # Get stats
        response = client.get('/api/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_users' in data
        assert isinstance(data['total_users'], int)
        assert data['total_users'] >= 1


class TestEmailTracking:
    """Test email tracking functionality"""
    
    def test_get_emails_unauthorized(self, client):
        """Test getting emails without authentication"""
        response = client.get('/api/emails')
        assert response.status_code == 401
    
    def test_get_emails_success(self, client, admin_token):
        """Test getting emails list with admin authentication"""
        response = client.get('/api/emails',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'emails' in data
        assert isinstance(data['emails'], list)


class TestIntegration:
    """Integration tests for complete user flow"""
    
    def test_complete_user_lifecycle(self, client, admin_token, clean_test_user):
        """Test complete user lifecycle: signup -> verify in dashboard -> check stats"""
        
        # Step 1: Sign up new user
        signup_response = client.post('/api/signup',
            json={
                'name': 'Integration Test User',
                'email': clean_test_user,
                'phone': '9876543210',
                'address': '789 Integration Blvd',
                'password': 'integrationpass123'
            },
            content_type='application/json'
        )
        assert signup_response.status_code == 201
        signup_data = json.loads(signup_response.data)
        user_id = signup_data['user_id']
        
        # Step 2: Verify user appears in users list
        users_response = client.get('/api/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert users_response.status_code == 200
        users_data = json.loads(users_response.data)
        
        user_found = False
        for user in users_data['users']:
            if user['email'] == clean_test_user:
                user_found = True
                assert user['name'] == 'Integration Test User'
                assert user['phone'] == '9876543210'
                assert user['address'] == '789 Integration Blvd'
                break
        
        assert user_found, "User not found in users list"
        
        # Step 3: Verify stats are updated
        stats_response = client.get('/api/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert stats_response.status_code == 200
        stats_data = json.loads(stats_response.data)
        assert stats_data['total_users'] >= 1
    
    def test_multiple_users_display(self, client, admin_token):
        """Test that multiple users are displayed correctly"""
        test_users = [
            {
                'name': 'User One',
                'email': f'user1_{datetime.now().timestamp()}@test.com',
                'phone': '1111111111',
                'address': 'Address 1',
                'password': 'pass123'
            },
            {
                'name': 'User Two',
                'email': f'user2_{datetime.now().timestamp()}@test.com',
                'phone': '2222222222',
                'address': 'Address 2',
                'password': 'pass123'
            },
            {
                'name': 'User Three',
                'email': f'user3_{datetime.now().timestamp()}@test.com',
                'phone': '3333333333',
                'address': 'Address 3',
                'password': 'pass123'
            }
        ]
        
        # Create users
        for user_data in test_users:
            response = client.post('/api/signup',
                json=user_data,
                content_type='application/json'
            )
            assert response.status_code == 201
        
        # Get users list
        response = client.get('/api/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify all users are present
        user_emails = [user['email'] for user in data['users']]
        for test_user in test_users:
            assert test_user['email'] in user_emails
        
        # Cleanup
        conn = get_db_connection()
        cursor = conn.cursor()
        for user_data in test_users:
            try:
                if USE_POSTGRES:
                    cursor.execute('DELETE FROM users WHERE email = %s', (user_data['email'],))
                else:
                    cursor.execute('DELETE FROM users WHERE email = ?', (user_data['email'],))
            except:
                pass
        conn.commit()
        conn.close()


def test_suite_summary():
    """Run all tests and provide summary"""
    print("\n" + "="*70)
    print("USER SIGNUP AND DASHBOARD TEST SUITE")
    print("="*70)
    print("\nTest Categories:")
    print("1. User Signup")
    print("   - Successful registration")
    print("   - Missing fields validation")
    print("   - Duplicate email handling")
    print("   - Password hashing")
    print("\n2. Dashboard Display")
    print("   - User list retrieval")
    print("   - Authentication required")
    print("   - Stats display")
    print("\n3. Email Tracking")
    print("   - Email list retrieval")
    print("\n4. Integration Tests")
    print("   - Complete user lifecycle")
    print("   - Multiple users handling")
    print("="*70)


if __name__ == '__main__':
    test_suite_summary()
    pytest.main([__file__, '-v', '--tb=short'])
