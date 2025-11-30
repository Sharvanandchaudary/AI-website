# XGenAI Application - Docker & GCP Deployment

Complete Flask application with PostgreSQL database, automated email exports, and GCP deployment ready.

## 🚀 Quick Start

### Local Development
```bash
# Start with Docker Compose
docker-compose up

# Access application
http://localhost:8080
```

### GCP Production Deployment
See **[GCP_DEPLOYMENT_GUIDE.md](GCP_DEPLOYMENT_GUIDE.md)** for complete step-by-step instructions.

## 📁 Project Structure

```
AI-website/
├── backend.py                    # Flask API server (2359 lines)
├── email_export.py              # Email export to Excel (154 lines)
├── xgenai-admin-dashboard.html  # Admin dashboard (1389 lines)
├── pages/
│   ├── signup.html              # User registration page
│   └── server-status.html       # Health check page
├── tests/
│   └── test_user_signup.py      # Test suite (12 tests, 93% coverage)
├── Dockerfile                    # Docker image configuration
├── docker-compose.yml           # Local development environment
├── crontab                      # Daily cron schedule (2 AM UTC)
├── requirements.txt             # Python dependencies
├── GCP_DEPLOYMENT_GUIDE.md      # Production deployment guide
└── LOCAL_TESTING.md             # Local testing guide
```

## ✨ Features

### Application Features
- ✅ User registration with validation
- ✅ Intern application submission
- ✅ Resume upload (stored in PostgreSQL BYTEA)
- ✅ Admin dashboard (users, applications, interns)
- ✅ Resume download from database
- ✅ Health check endpoint
- ✅ CORS support for API calls

### Email Export (NEW)
- ✅ **User Signups**: Exports name, email, phone, address to Excel
- ✅ **Intern Applications**: Exports name, email, phone, **job title**, college, degree, etc.
- ✅ Automated daily exports at 2 AM UTC
- ✅ Styled Excel files with headers
- ✅ Cloud Storage integration ready

### DevOps
- ✅ Docker containerization
- ✅ PostgreSQL 15 database
- ✅ Gunicorn production server (4 workers)
- ✅ Health checks every 30s
- ✅ CI/CD with GitHub Actions
- ✅ 12 automated tests (93% coverage)
- ✅ GCP Cloud Run ready

## 📊 Email Export Details

### User Signups Excel
Exports from `users` table:
- Full Name
- Email
- Phone
- Address
- Signup Date

### Intern Applications Excel
Exports from `applications` table:
- Full Name
- Email
- Phone
- **Job Title/Position** ← Position applied for
- College
- Degree
- Semester
- Year
- Status
- Applied Date
- LinkedIn Profile
- GitHub Profile

### Schedule
- **Frequency**: Daily at 2:00 AM UTC
- **Files**: `exports/user_signups_YYYYMMDD_HHMMSS.xlsx`
- **Files**: `exports/intern_applications_YYYYMMDD_HHMMSS.xlsx`

## 🐳 Docker Commands

### Local Development
```bash
# Build image
docker build -t xgenai-app .

# Run with docker-compose
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f web
```

### Test Email Export
```bash
# Run export manually
docker-compose exec web python email_export.py

# Check exports
ls -l exports/
```

## 🧪 Testing

### Run All Tests
```bash
# Unit tests
pytest tests/test_user_signup.py -v

# With coverage
pytest tests/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Manual Testing
See **[LOCAL_TESTING.md](LOCAL_TESTING.md)** for complete testing guide.

## 🌐 Deployment Options

### Option 1: Render (Current)
- Deployed at: https://ai-website-lzcx.onrender.com
- Auto-deploy from `main` branch
- PostgreSQL database included

### Option 2: Google Cloud Platform (Recommended)
- **Cost**: ~$15/month (dev) to ~$60-125/month (prod)
- **Services**: Cloud Run + Cloud SQL + Cloud Storage
- **Scaling**: Auto-scales 0-10 instances
- **Guide**: See [GCP_DEPLOYMENT_GUIDE.md](GCP_DEPLOYMENT_GUIDE.md)

## 📦 Dependencies

### Production
- Flask 3.0.0 (web framework)
- PostgreSQL (database)
- Gunicorn (WSGI server)
- openpyxl (Excel generation)
- psycopg2-binary (PostgreSQL driver)

### Development
- pytest (testing)
- pytest-cov (coverage)
- Docker & Docker Compose

## 🔒 Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ADMIN_EMAIL=admin@xgenai.com
ADMIN_PASSWORD=your_secure_password
PORT=8080
FLASK_ENV=production
```

## 📈 CI/CD Pipeline

GitHub Actions runs on every push:
1. **Unit Tests**: Backend functionality
2. **Integration Tests**: API endpoints
3. **E2E Tests**: Full user flows
4. **Security Scan**: Dependency vulnerabilities
5. **Deploy**: Auto-deploy to Render (main branch)

## 🚨 Recent Fixes

### v2.1.4 (Latest)
- ✅ Fixed deployment: Removed duplicate `/health` endpoint
- ✅ Added Docker configuration for GCP
- ✅ Implemented email export with Excel output
- ✅ Added daily cron job for automated exports

### v2.1.3
- ✅ Added user signup page with validation
- ✅ Created comprehensive test suite (12 tests)
- ✅ Integrated CI/CD pipeline

## 📚 Documentation

- **[GCP_DEPLOYMENT_GUIDE.md](GCP_DEPLOYMENT_GUIDE.md)** - Complete GCP deployment steps
- **[LOCAL_TESTING.md](LOCAL_TESTING.md)** - Local testing instructions
- **Admin Dashboard**: Full UI with light theme
- **API Documentation**: RESTful endpoints documented in backend.py

## 🆘 Troubleshooting

### Application Won't Start
```bash
# Check logs
docker-compose logs web

# Test database connection
docker-compose exec db psql -U postgres -c "SELECT 1;"
```

### Email Export Not Working
```bash
# Run manually
python email_export.py

# Check database has data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM applications;"
```

### Port Already in Use
```bash
# Stop all containers
docker-compose down

# Or change port in docker-compose.yml
ports:
  - "8081:8080"  # Use 8081 instead
```

## 📞 Support

- **GitHub**: https://github.com/Sharvanandchaudary/AI-website
- **Issues**: Create issue on GitHub
- **Email**: Check admin dashboard for contact

## 🎯 Next Steps

1. ✅ **Test Locally**: Follow [LOCAL_TESTING.md](LOCAL_TESTING.md)
2. 🚀 **Deploy to GCP**: Follow [GCP_DEPLOYMENT_GUIDE.md](GCP_DEPLOYMENT_GUIDE.md)
3. 📧 **Configure Email Export**: Set up Cloud Scheduler
4. 🔒 **Update Secrets**: Change default passwords
5. 📊 **Monitor**: Set up Cloud Monitoring alerts

---

**Version**: 2.1.4  
**Last Updated**: November 29, 2025  
**License**: MIT
