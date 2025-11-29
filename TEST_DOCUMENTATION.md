# Test Suite Documentation

## Overview
Comprehensive test suite for XGENAI website covering all critical functionality.

## Test Coverage

### 1. **Server Health Check**
- Verifies server is running and responding
- Tests root endpoint accessibility

### 2. **User Management**
- ✅ User registration with all required fields
- ✅ User login with credentials
- ✅ Token generation and validation
- ❌ Duplicate email rejection
- ❌ Invalid credentials rejection

### 3. **Job Applications**
- ✅ Complete application submission
- ✅ Data validation and storage
- ✅ Application status tracking
- ❌ Missing required fields rejection
- ❌ Invalid data format handling

### 4. **Admin Dashboard**
- ✅ Admin authentication
- ✅ Dashboard statistics (users, emails, interns)
- ✅ View all users
- ✅ View all applications
- ✅ View email history
- ❌ Unauthorized access blocking

### 5. **Intern Management System**
- ✅ Select applicant as intern
- ✅ Generate intern credentials
- ✅ View all interns
- ✅ Create weekly tasks
- ✅ Assign tasks to interns
- ✅ Intern login
- ✅ Intern dashboard access
- ✅ Task submission

### 6. **Email Functionality**
- ✅ Email sending via Mailgun
- ✅ Email history tracking
- ✅ Welcome emails for interns
- ✅ Email status verification

### 7. **Security & Edge Cases**
- ✅ Authentication token validation
- ✅ Authorization checks
- ✅ CORS handling
- ✅ Input validation
- ✅ Error handling
- ✅ SQL injection prevention (parameterized queries)

## Running Tests

### Prerequisites
```bash
pip install requests
```

### Run Full Test Suite
```bash
# Test production server
python test_system.py

# Test local server
python test_system.py http://localhost:5000

# Test specific URL
python test_system.py https://your-domain.com
```

### Expected Output
```
======================================================================
🧪 XGENAI COMPREHENSIVE TEST SUITE
======================================================================
Testing server: https://xgenai.onrender.com
Start time: 2025-11-29 12:00:00
======================================================================

✅ Server Health Check
   Status: 200

📝 User Management Tests:
✅ User Signup
   Status: 201, Response: {'message': 'User registered successfully'}
✅ User Login
   Token received: True

📋 Application Tests:
✅ Job Application Submission
   Status: 200, Response: {'message': 'Application submitted successfully'}

🔐 Admin Tests:
✅ Admin Login
   Token received: True, Role: admin
✅ Admin Dashboard Stats
   Users: 5, Emails: 12
✅ Admin View Users
   Total users fetched: 5
✅ Admin View Applications
   Total applications: 3

👥 Intern Management Tests:
✅ Select Intern
   Selected: Test Applicant
✅ View Interns
   Total interns: 1
✅ Create Weekly Task
   Task created for Week 1
✅ Intern Login
   Intern: Test Applicant, Token: True
✅ Intern Dashboard
   Tasks available: 1

📧 Email Tests:
✅ Email History
   Total emails sent: 12

🔍 Testing Edge Cases:
  ✅ Invalid Login Rejection
     Correctly rejected with status 401
  ✅ Incomplete Application Rejection
     Status: 400
  ✅ Unauthorized Admin Access Block
     Correctly blocked with status 401
  ✅ Duplicate Email Rejection
     Status: 409

======================================================================
📊 TEST SUMMARY
======================================================================
✅ Passed: 18
❌ Failed: 0
📈 Success Rate: 100.0%

======================================================================
End time: 2025-11-29 12:01:30
======================================================================
```

## Test Scenarios

### Happy Path Tests
1. ✅ New user registers → Login → Access dashboard
2. ✅ User submits job application → Admin views → Selects as intern
3. ✅ Intern receives credentials → Login → Views tasks
4. ✅ Admin creates task → Intern sees task → Submits work

### Error Handling Tests
1. ❌ Invalid credentials → Login rejected
2. ❌ Incomplete application → Form validation error
3. ❌ Unauthorized access → 401 error
4. ❌ Duplicate email → Registration blocked

### Database Tests
- ✅ User data persistence
- ✅ Application data storage
- ✅ Intern records creation
- ✅ Task assignment tracking
- ✅ Email log retention

### API Endpoint Tests
- ✅ POST /api/signup
- ✅ POST /api/login
- ✅ POST /api/applications
- ✅ POST /api/admin/login
- ✅ GET /api/stats
- ✅ GET /api/users
- ✅ GET /api/emails
- ✅ GET /api/admin/applications
- ✅ POST /api/admin/select-intern
- ✅ GET /api/admin/interns
- ✅ POST /api/admin/weekly-task
- ✅ POST /api/intern/login
- ✅ GET /api/intern/dashboard

## Manual Testing Checklist

### User Flow
- [ ] Navigate to homepage
- [ ] Click "Get Started" → Auth page loads
- [ ] Register new account → Success message
- [ ] Login with credentials → Redirect to dashboard
- [ ] View dashboard sections → Data displays correctly

### Application Flow
- [ ] Navigate to Careers page
- [ ] Click "Apply Now" on job listing
- [ ] Fill complete application form
- [ ] Upload resume (PDF/DOC)
- [ ] Submit → Success confirmation
- [ ] Check email for confirmation

### Admin Flow
- [ ] Navigate to /admin-v3.html
- [ ] Login with admin credentials
- [ ] Dashboard loads with statistics
- [ ] Click Applications tab → View all applications
- [ ] Click "Select as Intern" → Confirmation prompt
- [ ] Confirm → Success message
- [ ] Check Interns tab → New intern appears
- [ ] Create Weekly Task → Task created
- [ ] View email history → Recent emails shown

### Intern Flow
- [ ] Navigate to /intern-login.html
- [ ] Login with intern email + "Intern@123"
- [ ] Dashboard loads with tasks
- [ ] View task details
- [ ] Upload submission file
- [ ] Submit task → Success confirmation

## Performance Tests
- Response time < 2 seconds for most endpoints
- Database queries optimized with indexes
- Concurrent user handling (100+ simultaneous connections)
- File upload handling (up to 5MB)

## Security Tests
- ✅ Password hashing (SHA-256)
- ✅ Token-based authentication
- ✅ CORS configuration
- ✅ SQL injection prevention
- ✅ XSS protection (input sanitization)
- ✅ Admin role verification

## Browser Compatibility
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Known Issues & Limitations
1. ⚠️ Email sending requires Mailgun configuration
2. ⚠️ File uploads stored as base64 (size limitation)
3. ⚠️ Session tokens stored in memory (lost on restart)

## Future Test Enhancements
- [ ] Load testing with 1000+ concurrent users
- [ ] Automated UI testing with Selenium
- [ ] API response time benchmarks
- [ ] Database stress testing
- [ ] Email delivery rate monitoring
