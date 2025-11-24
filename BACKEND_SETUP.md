# Backend Setup Guide

## 🗄️ Database-Backed AI Solutions Website

Your website now has a **real backend server** with **SQLite database** that stores data permanently!

---

## 📦 What's Included:

### Backend Server (`backend.py`)
- ✅ Flask REST API server
- ✅ SQLite database for permanent storage
- ✅ User authentication with password hashing
- ✅ Email notification system
- ✅ Session management
- ✅ Admin API endpoints

### Database (`aisolutions.db`)
Three tables:
1. **users** - Store all registered users
2. **emails** - Store all confirmation emails
3. **sessions** - Store user login sessions

---

## 🚀 How to Run:

### Step 1: Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend Server
```bash
python backend.py
```

You'll see:
```
✅ Database initialized successfully!
🚀 AI Solutions Backend Server
📍 Server running at: http://localhost:5000
📊 Admin Dashboard: http://localhost:5000/admin.html
🔐 Auth Page: http://localhost:5000/auth.html
💾 Database: aisolutions.db
```

### Step 3: Access Your Website
- **Main Website**: http://localhost:5000
- **Login/Signup**: http://localhost:5000/auth.html
- **Admin Dashboard**: http://localhost:5000/admin.html

---

## 💾 Data Storage:

### **LOCAL (Development)**
- Database file: `aisolutions.db`
- Location: Same folder as backend.py
- Persists even after server restart
- Can be backed up easily

### **PRODUCTION (Hosted)**
When you deploy to production:

1. **Hosting Options:**
   - Heroku (Free tier available)
   - AWS EC2
   - Google Cloud
   - DigitalOcean
   - Azure

2. **Database Options:**
   - SQLite (for small apps)
   - PostgreSQL (recommended for production)
   - MySQL
   - MongoDB

3. **What Happens:**
   - Backend server runs 24/7 on cloud
   - Database hosted on cloud server
   - Users from anywhere can access
   - Data syncs in real-time
   - Automatic backups

---

## 🔄 Local vs Production:

### **Development (Current Setup)**
```
Your Computer
├── backend.py (Flask server)
└── aisolutions.db (SQLite database)
     ├── users table
     ├── emails table
     └── sessions table
```

### **Production (Hosted)**
```
Cloud Server (e.g., Heroku)
├── backend.py (Flask server - always running)
└── Database (PostgreSQL/MySQL)
     ├── users table
     ├── emails table
     └── sessions table

Users → Internet → Your Domain → Cloud Server → Database
```

---

## 📧 Email Configuration:

To send **real emails**, update in `backend.py`:

```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

For Gmail:
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate App Password
4. Use that password in code

Then uncomment lines 62-67 in `backend.py`:
```python
msg = Message(
    'Welcome to AI Solutions - Account Created Successfully!',
    recipients=[user_data['email']],
    body=email_body
)
mail.send(msg)
```

---

## 🔒 Security Features:

✅ **Password Hashing** - Passwords stored as SHA-256 hash
✅ **Session Tokens** - Secure login sessions
✅ **Input Validation** - All fields validated
✅ **SQL Injection Protection** - Parameterized queries
✅ **CORS Enabled** - Cross-origin requests allowed

---

## 📊 API Endpoints:

### User Authentication:
- `POST /api/signup` - Register new user
- `POST /api/login` - Login user

### Admin:
- `GET /api/users` - Get all users
- `GET /api/emails` - Get all emails
- `GET /api/stats` - Get statistics
- `DELETE /api/clear-data` - Clear all data

---

## 🗂️ Database Schema:

### Users Table:
```sql
id              INTEGER PRIMARY KEY
name            TEXT NOT NULL
email           TEXT UNIQUE NOT NULL
phone           TEXT NOT NULL
address         TEXT NOT NULL
password_hash   TEXT NOT NULL
created_at      TIMESTAMP
last_login      TIMESTAMP
```

### Emails Table:
```sql
id          INTEGER PRIMARY KEY
to_email    TEXT NOT NULL
subject     TEXT NOT NULL
body        TEXT NOT NULL
sent_at     TIMESTAMP
user_id     INTEGER (Foreign Key)
```

### Sessions Table:
```sql
id          INTEGER PRIMARY KEY
user_id     INTEGER NOT NULL
token       TEXT UNIQUE NOT NULL
created_at  TIMESTAMP
```

---

## 🔄 Switching Between Storage:

### Use LocalStorage (Browser):
In HTML files, use:
```html
<script src="auth.js"></script>
```

### Use Backend Database:
In HTML files, use:
```html
<script src="auth-backend.js"></script>
```

Currently set to: **Backend Database** ✅

---

## 📈 Production Deployment Guide:

### Deploy to Heroku (Free):

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Add Procfile**
   ```
   web: python backend.py
   ```

4. **Deploy**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. **Your website is now live!**
   ```
   https://your-app-name.herokuapp.com
   ```

---

## 🛠️ Maintenance:

### Backup Database:
```bash
# Copy the database file
copy aisolutions.db aisolutions_backup.db
```

### View Database:
```bash
# Install SQLite browser
# Or use command line:
sqlite3 aisolutions.db
.tables
SELECT * FROM users;
```

### Clear All Data:
```bash
# Delete database file
del aisolutions.db

# Restart server to recreate empty database
python backend.py
```

---

## ❓ FAQ:

**Q: Where is my data stored now?**
A: In `aisolutions.db` file in your project folder.

**Q: Will data persist after restart?**
A: Yes! Database file keeps all data permanently.

**Q: Can multiple users access at once?**
A: Yes, SQLite supports concurrent reads.

**Q: How to move to production?**
A: Deploy backend to cloud hosting (Heroku, AWS, etc.)

**Q: Is it secure?**
A: Yes for development. For production, add HTTPS and stronger auth.

---

## 📞 Support:

For issues or questions:
1. Check console for errors (F12)
2. Check terminal for backend logs
3. Verify database file exists
4. Ensure port 5000 is not in use

---

**🎉 Your website now has a professional backend with database storage!**
