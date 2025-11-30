# CI/CD Test Configuration

## Test Pipeline Overview

The CI/CD pipeline now includes comprehensive testing with three test suites:

### Test Execution Order

1. **Unit Tests** (`tests/test_basic.py`)
   - Basic functionality validation
   - API endpoint structure tests
   - Database connection tests

2. **User Signup Tests** (`tests/test_user_signup.py`) ⭐ NEW
   - User registration flow (4 tests)
   - Admin dashboard display (3 tests)
   - Email tracking (2 tests)
   - Integration tests (2 tests)
   - **Total: 12 tests with 93% coverage**

3. **End-to-End Tests** (`tests/test_e2e_cicd.py`)
   - Complete application flow validation
   - Critical path testing

## What Gets Tested

### User Signup & Dashboard Tests (New)
```yaml
- test_signup_success                 # ✅ User registration
- test_signup_missing_fields          # ✅ Field validation
- test_signup_duplicate_email         # ✅ Duplicate prevention
- test_password_hashing               # ✅ Security check
- test_get_users_unauthorized         # ✅ Auth required
- test_get_users_success              # ✅ Dashboard display
- test_stats_include_users            # ✅ Statistics
- test_get_emails_unauthorized        # ✅ Email auth
- test_get_emails_success             # ✅ Email tracking
- test_complete_user_lifecycle        # ✅ Full flow
- test_multiple_users_display         # ✅ Multiple users
- test_suite_summary                  # ✅ Summary
```

## CI/CD Workflow Files

### 1. `.github/workflows/ci-cd.yml` (Main Pipeline)
**Trigger**: Push to main, Pull requests
**Jobs**:
- ✅ Test (runs all test suites)
- ✅ Deploy (only on main branch)

**Test Steps**:
```yaml
1. Run Unit Tests           → tests/test_basic.py
2. Run User Signup Tests    → tests/test_user_signup.py (NEW)
3. Run E2E Tests            → tests/test_e2e_cicd.py
4. Security Checks          → Bandit, Safety
5. Coverage Upload          → Codecov
```

### 2. `.github/workflows/deploy.yml` (Production Deploy)
**Trigger**: Push to main
**Jobs**:
- ✅ Run all tests before deploy
- ✅ Deploy to Render
- ✅ Deploy to Vercel (optional)

## Test Reports Generated

After each CI/CD run, these reports are available:

1. `unit-test-report.html` - Unit test results
2. `user-signup-test-report.html` - User signup test results ⭐ NEW
3. `e2e-test-report.html` - End-to-end test results
4. `htmlcov/` - Code coverage report

All reports are uploaded as GitHub Actions artifacts.

## Coverage Targets

| Test Suite | Coverage | Status |
|------------|----------|--------|
| Unit Tests | Variable | ✅ Pass |
| User Signup Tests | 93% | ✅ Pass |
| E2E Tests | Variable | ✅ Pass |
| Overall Backend | 29% | 🔄 Improving |

## Running Tests Locally

### Run All Tests
```bash
pytest -v
```

### Run User Signup Tests Only
```bash
pytest tests/test_user_signup.py -v
```

### Run with Coverage
```bash
pytest tests/test_user_signup.py -v --cov=backend --cov-report=html
```

### Run All CI Tests (Same as CI/CD)
```bash
pytest tests/test_basic.py tests/test_user_signup.py tests/test_e2e_cicd.py -v
```

## CI/CD Status Checks

GitHub will show status checks for:
- ✅ **Unit Tests** - Must pass
- ✅ **User Signup Tests** - Must pass (NEW)
- ✅ **E2E Tests** - Must pass
- ⚠️ **Security Checks** - Warnings allowed
- ⚠️ **Integration Tests** - Skipped in CI

## Deployment Flow

```
Code Push to Main
    ↓
Run Unit Tests
    ↓
Run User Signup Tests (NEW)
    ↓
Run E2E Tests
    ↓
Security Checks
    ↓
All Tests Pass?
    ↓ Yes
Deploy to Render
    ↓
Health Check
    ↓
✅ Live!
```

## Environment Requirements

### Required in CI/CD:
- Python 3.11
- pytest
- pytest-cov
- pytest-html
- All dependencies from requirements.txt

### Optional Secrets:
- `RENDER_API_KEY` (auto-deploy enabled)
- `VERCEL_TOKEN` (if using Vercel)
- `CODECOV_TOKEN` (for coverage reports)

## Test Failure Handling

| Failure Type | Action |
|--------------|--------|
| Unit Test Fail | ❌ Block deployment |
| User Signup Test Fail | ❌ Block deployment |
| E2E Test Fail | ❌ Block deployment |
| Security Warning | ⚠️ Continue with warning |
| Integration Test | ℹ️ Skipped (requires running server) |

## Viewing Test Results

### In GitHub Actions:
1. Go to repository → Actions tab
2. Click on latest workflow run
3. View test summary in logs
4. Download test artifacts for detailed reports

### Test Artifacts Include:
- HTML test reports
- Coverage reports
- Security scan results

## Next Steps for CI/CD Enhancement

1. **Add Integration Tests to CI**
   - Spin up test database
   - Run full integration tests

2. **Add Performance Tests**
   - Load testing
   - Response time checks

3. **Add Frontend Tests**
   - Selenium/Playwright tests
   - Component testing

4. **Add Automated Deployment Notifications**
   - Slack/Discord webhooks
   - Email notifications

## Monitoring

After deployment, CI/CD performs:
- ✅ Health check (curl to homepage)
- ✅ 60-second wait for Render deployment
- ✅ Success notification

## Status Badge

Add to README.md:
```markdown
![CI/CD Pipeline](https://github.com/Sharvanandchaudary/AI-website/workflows/CI%2FCD%20Pipeline%20-%20Test%20%26%20Deploy/badge.svg)
```

---

**Last Updated**: November 29, 2025  
**Pipeline Status**: ✅ Active with User Signup Tests Integrated  
**Test Count**: 12+ user tests + existing unit/e2e tests
