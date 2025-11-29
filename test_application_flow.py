"""Test application submission flow"""
import requests
import json

# Test configuration
API_URL = "http://localhost:5000"  # Change to your Render URL when testing production

def test_application_submission():
    """Test submitting a job application"""
    
    application_data = {
        "position": "AI Intern",
        "fullName": "Test Candidate",
        "email": "test@example.com",
        "phone": "+1234567890",
        "address": "123 Test Street, Test City, TC 12345",
        "college": "Test University",
        "degree": "B.Tech in Computer Science",
        "semester": "6th",
        "year": "2026",
        "about": "I am passionate about AI and machine learning. I have experience with Python, TensorFlow, and building ML models.",
        "resumeName": "test_resume.pdf",
        "linkedin": "https://linkedin.com/in/testuser",
        "github": "https://github.com/testuser"
    }
    
    print("\n" + "="*60)
    print("🧪 Testing Application Submission")
    print("="*60)
    
    try:
        # Submit application
        print(f"\n📤 Submitting application to: {API_URL}/api/applications")
        response = requests.post(
            f"{API_URL}/api/applications",
            headers={"Content-Type": "application/json"},
            json=application_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            result = response.json()
            print("\n✅ SUCCESS! Application submitted successfully")
            print(f"   Application ID: {result.get('application_id')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"\n❌ FAILED! Status: {response.status_code}")
            print(f"   Error: {response.json().get('error')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Could not connect to {API_URL}")
        print("   Make sure the Flask server is running!")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_application_submission()
    exit(0 if success else 1)
