# Local Testing Guide

Quick guide to test the application and email export functionality locally before deploying to GCP.

## 📦 Prerequisites

- Python 3.11+
- Docker Desktop (for containerized testing)
- PostgreSQL (or use docker-compose)

## 🧪 Method 1: Test with Docker Compose (Recommended)

### Start Application

```bash
# Start all services (Flask app + PostgreSQL)
docker-compose up

# Application runs at: http://localhost:8080
# Admin dashboard: http://localhost:8080/admin-login.html
# Signup page: http://localhost:8080/pages/signup.html
```

### Test Email Export

```bash
# In another terminal, run email export
docker-compose exec web python email_export.py

# Check exports directory
ls -l exports/
# Should see: user_signups_YYYYMMDD_HHMMSS.xlsx
#             intern_applications_YYYYMMDD_HHMMSS.xlsx

# Stop services
docker-compose down
```

## 🐍 Method 2: Test with Python Virtual Environment

### Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Start PostgreSQL

```bash
# Option 1: Docker PostgreSQL only
docker run -d \
  --name xgenai-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=xgenai \
  -p 5432:5432 \
  postgres:15-alpine

# Option 2: Local PostgreSQL installation
# (Configure connection in .env file)
```

### Configure Environment

Create `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/xgenai
ADMIN_EMAIL=admin@xgenai.com
ADMIN_PASSWORD=Admin@123
PORT=8080
FLASK_ENV=development
```

### Start Application

```bash
# Run Flask app
python backend.py

# Application runs at: http://localhost:8080
```

### Test Email Export

```bash
# In another terminal (with venv activated)
python email_export.py

# Check exports directory
dir exports\         # Windows
ls -l exports/       # Mac/Linux

# Open Excel files to verify data
```

## ✅ Test Checklist

### 1. Health Check

```bash
curl http://localhost:8080/health
# Expected: {"status": "healthy", "database": "connected"}
```

### 2. Test User Signup

```bash
curl -X POST http://localhost:8080/api/signup \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"phone\":\"1234567890\",\"address\":\"Test Address\",\"password\":\"test123\"}"

# Expected: {"message": "User created successfully"}
```

### 3. Test Admin Login

```bash
curl -X POST http://localhost:8080/api/admin/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@xgenai.com\",\"password\":\"Admin@123\"}"

# Expected: {"message": "Login successful"}
```

### 4. Test Intern Application

```bash
# Apply for internship
curl -X POST http://localhost:8080/api/applications \
  -F "full_name=John Doe" \
  -F "email=john@example.com" \
  -F "phone=9876543210" \
  -F "job_title=Software Engineer" \
  -F "college=MIT" \
  -F "degree=B.Tech" \
  -F "semester=6" \
  -F "year=3" \
  -F "linkedin=https://linkedin.com/in/johndoe" \
  -F "github=https://github.com/johndoe" \
  -F "resume=@sample-resume.pdf"

# Expected: {"message": "Application submitted successfully"}
```

### 5. Verify Data in Database

```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres@localhost:5432/xgenai

# Check users
SELECT COUNT(*) FROM users;
SELECT name, email FROM users;

# Check applications
SELECT COUNT(*) FROM applications;
SELECT full_name, email, position FROM applications;

# Exit
\q
```

### 6. Test Email Export

```bash
# Run export script
python email_export.py

# Verify output files
dir exports\                          # Windows
ls -l exports/                        # Mac/Linux

# Expected files:
# - user_signups_20251129_143052.xlsx
# - intern_applications_20251129_143052.xlsx

# Open files in Excel to verify:
# User signups: name, email, phone, address, signup date
# Applications: name, email, phone, JOB TITLE, college, degree, etc.
```

## 🔍 Verify Email Export Content

### User Signups Excel

Should contain columns:
- Full Name
- Email
- Phone
- Address
- Signup Date

### Intern Applications Excel

Should contain columns:
- Full Name
- Email
- Phone
- **Job Title/Position** ← Important: job title from application
- College
- Degree
- Semester
- Year
- Status
- Applied Date
- LinkedIn
- GitHub

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker ps                           # If using Docker
systemctl status postgresql         # If using system PostgreSQL

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Import Error: No module named 'openpyxl'

```bash
# Install missing dependencies
pip install openpyxl schedule
```

### Permission Denied: exports/

```bash
# Create exports directory
mkdir exports

# Or in PowerShell
New-Item -ItemType Directory -Force -Path exports
```

### Empty Excel Files

```bash
# Check if data exists in database
psql $DATABASE_URL

# Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM applications;

# If zero, create test data (see Test Checklist above)
```

## 🚀 Build and Test Docker Image

### Build Local Image

```bash
# Build image
docker build -t xgenai-test:local .

# Run container
docker run -d \
  --name xgenai-test \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/xgenai" \
  -e ADMIN_EMAIL="admin@xgenai.com" \
  -e ADMIN_PASSWORD="Admin@123" \
  xgenai-test:local

# View logs
docker logs -f xgenai-test

# Test application
curl http://localhost:8080/health

# Stop and remove
docker stop xgenai-test
docker rm xgenai-test
```

### Test Cron Job in Container

```bash
# Start container with shell
docker run -it \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/xgenai" \
  xgenai-test:local \
  /bin/bash

# Inside container, test cron
crontab /etc/cron.d/email-export-cron
crontab -l

# Manually trigger export
python email_export.py

# Check exports
ls -l exports/

# Exit
exit
```

## 📊 Performance Testing

### Load Test (Optional)

```bash
# Install Apache Bench
apt-get install apache2-utils    # Linux
brew install apache2-utils        # Mac

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8080/health

# Test signup endpoint
ab -n 100 -c 5 -p signup.json -T application/json http://localhost:8080/api/signup
```

## ✨ Tips

1. **Always test email export after adding test data** to verify Excel format
2. **Check Excel files manually** to ensure job titles appear correctly
3. **Test with multiple users and applications** to verify all data exports
4. **Monitor logs** for any errors during export: `tail -f /var/log/cron.log`
5. **Use docker-compose** for easiest local testing experience

## 🔄 Next Steps

Once local testing is complete:

1. ✅ Verify all features work locally
2. ✅ Check Excel exports contain correct data
3. 🚀 Follow **GCP_DEPLOYMENT_GUIDE.md** to deploy to production
4. 🔒 Update passwords and secrets in GCP Secret Manager
5. 📧 Configure Cloud Scheduler for daily exports

---

**Ready to Deploy?** See `GCP_DEPLOYMENT_GUIDE.md` for production deployment steps!
