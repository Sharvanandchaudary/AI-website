# AI Solutions - Professional AI/ML/Data Platform

A modern, production-ready SaaS platform for AI Solutions, Data Analytics, and Machine Learning services with full user authentication, admin dashboard, and email notifications.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python backend.py

# Open browser
http://localhost:5000
```

## 🌐 Deploy to Production

### Option 1: Render (Recommended - Free Tier Available)

1. Push code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn backend:app`
6. Add PostgreSQL database
7. Your site is live at `https://yourapp.onrender.com`

### Option 2: Heroku

```bash
heroku create your-app
heroku addons:create heroku-postgresql
git push heroku main
```

## 📦 What's Included

- ✅ Modern landing page with animations
- ✅ User authentication (signup/login)
- ✅ Email confirmations
- ✅ Admin dashboard
- ✅ Database (SQLite dev / PostgreSQL prod)
- ✅ Production-ready backend
- ✅ GitHub Actions CI/CD
- ✅ Mobile responsive

## 🗄️ Data Storage

### Development
- **Local**: SQLite database file (`aisolutions.db`)
- **Location**: Project folder

### Production  
- **Cloud**: PostgreSQL database
- **Hosting**: Render/Heroku servers
- **Access**: Worldwide
- **Backup**: Automatic
- **Persistence**: Permanent

## 📧 Email Setup

1. Use Gmail with App Password
2. Add to environment variables:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

## 🔐 Security

- Password hashing (SHA-256)
- Session tokens
- Environment variables for secrets
- CORS protection
- SQL injection prevention

## 📊 Features

### User Side
- Create account with name, email, phone, address
- Receive confirmation email
- Secure login with password
- View all solutions

### Admin Side  
- View all registered users
- See all emails sent
- Real-time statistics
- Manage users

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Database**: SQLite / PostgreSQL
- **Email**: Flask-Mail
- **Deploy**: Render / Heroku

## 📁 Files

```
backend.py          - Main server
index.html          - Landing page
auth.html           - Login/Signup
admin.html          - Admin dashboard
styles.css          - Styles
requirements.txt    - Dependencies
Procfile           - Deploy config
.github/workflows  - CI/CD pipeline
```

## 🚀 GitHub Deployment

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ai-website.git
git push -u origin main
```

Then connect to Render/Heroku via dashboard.

## 📖 Full Documentation

See `PRODUCTION_SETUP.md` for detailed deployment instructions.

---

**Questions?** Check the detailed guides in the project files!
