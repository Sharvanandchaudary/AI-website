"""
Comprehensive Test Suite for XGENAI Website
Tests all critical functionality including:
- User registration and authentication
- Job application submission
- Admin authentication and dashboard
- Intern management system
- Email functionality
- Database operations
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://xgenai.onrender.com"  # Change to local for testing: http://localhost:5000
ADMIN_EMAIL = "admin@zgenai.com"
ADMIN_PASSWORD = "Admin@123"

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def print_test(test_name, status, message=""):
    """Print test result with formatting"""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {test_name}")
    if message:
        print(f"   {message}")
    if status:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{test_name}: {message}")

def test_health_check():
    """Test 1: Server health check"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print_test("Server Health Check", response.status_code == 200, 
                   f"Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print_test("Server Health Check", False, str(e))
        return False

def test_user_signup():
    """Test 2: User registration"""
    try:
        user_data = {
            "name": "Test User",
            "email": f"test_{int(time.time())}@example.com",
            "phone": "1234567890",
            "address": "123 Test St, Test City",
            "password": "TestPass123!"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/signup",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        success = response.status_code == 201 or response.status_code == 200
        print_test("User Signup", success, 
                   f"Status: {response.status_code}, Response: {response.json()}")
        return success, user_data
    except Exception as e:
        print_test("User Signup", False, str(e))
        return False, None

def test_user_login(user_data):
    """Test 3: User login"""
    try:
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        success = response.status_code == 200 and result.get('success', False)
        print_test("User Login", success, 
                   f"Token received: {bool(result.get('token'))}")
        return success, result.get('token')
    except Exception as e:
        print_test("User Login", False, str(e))
        return False, None

def test_job_application():
    """Test 4: Job application submission"""
    try:
        application_data = {
            "position": "AI/ML Intern",
            "fullName": "Test Applicant",
            "email": f"applicant_{int(time.time())}@example.com",
            "phone": "9876543210",
            "address": "456 Apply St, Application City",
            "college": "Test University",
            "degree": "B.Tech Computer Science",
            "semester": "6th",
            "year": "2025",
            "about": "Passionate about AI and machine learning. Test application.",
            "linkedin": "https://linkedin.com/in/testuser",
            "github": "https://github.com/testuser",
            "resumeName": "test_resume.pdf"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/applications",
            json=application_data,
            headers={"Content-Type": "application/json"}
        )
        
        success = response.status_code == 200 or response.status_code == 201
        print_test("Job Application Submission", success, 
                   f"Status: {response.status_code}, Response: {response.json()}")
        return success, application_data
    except Exception as e:
        print_test("Job Application Submission", False, str(e))
        return False, None

def test_admin_login():
    """Test 5: Admin login"""
    try:
        admin_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        success = response.status_code == 200 and result.get('success', False)
        token = result.get('token')
        print_test("Admin Login", success, 
                   f"Token received: {bool(token)}, Role: {result.get('role')}")
        return success, token
    except Exception as e:
        print_test("Admin Login", False, str(e))
        return False, None

def test_admin_stats(admin_token):
    """Test 6: Admin dashboard statistics"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/stats",
            headers={"Authorization": admin_token}
        )
        
        result = response.json()
        success = response.status_code == 200
        print_test("Admin Dashboard Stats", success, 
                   f"Users: {result.get('total_users', 0)}, Emails: {result.get('total_emails', 0)}")
        return success
    except Exception as e:
        print_test("Admin Dashboard Stats", False, str(e))
        return False

def test_admin_users(admin_token):
    """Test 7: View all users (admin)"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/users",
            headers={"Authorization": admin_token}
        )
        
        result = response.json()
        success = response.status_code == 200
        users_count = len(result.get('users', []))
        print_test("Admin View Users", success, 
                   f"Total users fetched: {users_count}")
        return success
    except Exception as e:
        print_test("Admin View Users", False, str(e))
        return False

def test_admin_applications(admin_token):
    """Test 8: View all applications (admin)"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/applications",
            headers={"Authorization": admin_token}
        )
        
        result = response.json()
        success = response.status_code == 200
        apps_count = len(result.get('applications', []))
        print_test("Admin View Applications", success, 
                   f"Total applications: {apps_count}")
        return success, result.get('applications', [])
    except Exception as e:
        print_test("Admin View Applications", False, str(e))
        return False, []

def test_select_intern(admin_token, applications):
    """Test 9: Select applicant as intern"""
    if not applications:
        print_test("Select Intern", False, "No applications available to select")
        return False
    
    try:
        # Get first pending application
        app = next((a for a in applications if a.get('status') == 'pending'), None)
        if not app:
            print_test("Select Intern", False, "No pending applications")
            return False
        
        response = requests.post(
            f"{BASE_URL}/api/admin/select-intern",
            json={
                "application_id": app['id'],
                "default_password": "Intern@123"
            },
            headers={
                "Authorization": admin_token,
                "Content-Type": "application/json"
            }
        )
        
        success = response.status_code == 200
        print_test("Select Intern", success, 
                   f"Selected: {app.get('full_name', 'Unknown')}")
        return success
    except Exception as e:
        print_test("Select Intern", False, str(e))
        return False

def test_view_interns(admin_token):
    """Test 10: View all interns"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/interns",
            headers={"Authorization": admin_token}
        )
        
        result = response.json()
        success = response.status_code == 200
        interns_count = len(result.get('interns', []))
        print_test("View Interns", success, 
                   f"Total interns: {interns_count}")
        return success, result.get('interns', [])
    except Exception as e:
        print_test("View Interns", False, str(e))
        return False, []

def test_create_weekly_task(admin_token):
    """Test 11: Create weekly task for interns"""
    try:
        task_data = {
            "week_number": 1,
            "title": "Test Task - Week 1",
            "description": "This is a test task description",
            "mini_project": "Build a simple calculator",
            "ds_algo": "Arrays and Sorting",
            "ai_news": "Latest developments in GPT models"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/weekly-task",
            json=task_data,
            headers={
                "Authorization": admin_token,
                "Content-Type": "application/json"
            }
        )
        
        success = response.status_code == 200 or response.status_code == 201
        print_test("Create Weekly Task", success, 
                   f"Task created for Week {task_data['week_number']}")
        return success
    except Exception as e:
        print_test("Create Weekly Task", False, str(e))
        return False

def test_intern_login(interns):
    """Test 12: Intern login"""
    if not interns:
        print_test("Intern Login", False, "No interns available to test login")
        return False, None
    
    try:
        intern = interns[0]
        login_data = {
            "email": intern['email'],
            "password": "Intern@123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/intern/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        success = response.status_code == 200 and result.get('success', False)
        print_test("Intern Login", success, 
                   f"Intern: {intern['name']}, Token: {bool(result.get('token'))}")
        return success, result.get('token')
    except Exception as e:
        print_test("Intern Login", False, str(e))
        return False, None

def test_intern_dashboard(intern_token):
    """Test 13: Intern dashboard"""
    if not intern_token:
        print_test("Intern Dashboard", False, "No intern token available")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/intern/dashboard",
            headers={"Authorization": intern_token}
        )
        
        result = response.json()
        success = response.status_code == 200
        tasks_count = len(result.get('tasks', []))
        print_test("Intern Dashboard", success, 
                   f"Tasks available: {tasks_count}")
        return success
    except Exception as e:
        print_test("Intern Dashboard", False, str(e))
        return False

def test_email_functionality(admin_token):
    """Test 14: Email history"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/emails",
            headers={"Authorization": admin_token}
        )
        
        result = response.json()
        success = response.status_code == 200
        emails_count = len(result.get('emails', []))
        print_test("Email History", success, 
                   f"Total emails sent: {emails_count}")
        return success
    except Exception as e:
        print_test("Email History", False, str(e))
        return False

def test_edge_cases():
    """Test 15: Edge cases and error handling"""
    print("\n🔍 Testing Edge Cases:")
    
    # Test 1: Invalid login
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"email": "invalid@test.com", "password": "wrong"},
            headers={"Content-Type": "application/json"}
        )
        success = response.status_code == 401
        print_test("  Invalid Login Rejection", success, 
                   f"Correctly rejected with status {response.status_code}")
    except Exception as e:
        print_test("  Invalid Login Rejection", False, str(e))
    
    # Test 2: Missing required fields in application
    try:
        response = requests.post(
            f"{BASE_URL}/api/applications",
            json={"fullName": "Incomplete", "email": "test@test.com"},
            headers={"Content-Type": "application/json"}
        )
        success = response.status_code == 400
        print_test("  Incomplete Application Rejection", success, 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("  Incomplete Application Rejection", False, str(e))
    
    # Test 3: Unauthorized access to admin endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/admin/applications")
        success = response.status_code == 401
        print_test("  Unauthorized Admin Access Block", success, 
                   f"Correctly blocked with status {response.status_code}")
    except Exception as e:
        print_test("  Unauthorized Admin Access Block", False, str(e))
    
    # Test 4: Duplicate email registration
    try:
        duplicate_user = {
            "name": "Duplicate",
            "email": ADMIN_EMAIL,  # Try to register with admin email
            "phone": "1111111111",
            "address": "Test",
            "password": "Test123"
        }
        response = requests.post(
            f"{BASE_URL}/api/signup",
            json=duplicate_user,
            headers={"Content-Type": "application/json"}
        )
        success = response.status_code in [400, 409]  # Should reject duplicate
        print_test("  Duplicate Email Rejection", success, 
                   f"Status: {response.status_code}")
    except Exception as e:
        print_test("  Duplicate Email Rejection", False, str(e))

def run_all_tests():
    """Run complete test suite"""
    print("=" * 70)
    print("🧪 XGENAI COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Testing server: {BASE_URL}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Test 1: Server Health
    if not test_health_check():
        print("\n❌ Server is not responding. Cannot continue tests.")
        return
    
    print("\n📝 User Management Tests:")
    # Test 2-3: User signup and login
    signup_success, user_data = test_user_signup()
    if signup_success and user_data:
        test_user_login(user_data)
    
    print("\n📋 Application Tests:")
    # Test 4: Job application
    test_job_application()
    
    print("\n🔐 Admin Tests:")
    # Test 5: Admin login
    admin_success, admin_token = test_admin_login()
    
    if admin_success and admin_token:
        # Test 6-8: Admin dashboard
        test_admin_stats(admin_token)
        test_admin_users(admin_token)
        apps_success, applications = test_admin_applications(admin_token)
        
        print("\n👥 Intern Management Tests:")
        # Test 9-11: Intern management
        if apps_success:
            test_select_intern(admin_token, applications)
        
        interns_success, interns = test_view_interns(admin_token)
        test_create_weekly_task(admin_token)
        
        # Test 12-13: Intern functionality
        if interns_success and interns:
            intern_success, intern_token = test_intern_login(interns)
            if intern_success and intern_token:
                test_intern_dashboard(intern_token)
        
        print("\n📧 Email Tests:")
        # Test 14: Email functionality
        test_email_functionality(admin_token)
    
    # Test 15: Edge cases
    test_edge_cases()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📈 Success Rate: {(test_results['passed'] / (test_results['passed'] + test_results['failed']) * 100):.1f}%")
    
    if test_results['errors']:
        print("\n❌ Failed Tests:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    print("\n" + "=" * 70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    # Check if custom URL provided
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip('/')
        print(f"Using custom URL: {BASE_URL}")
    
    run_all_tests()
