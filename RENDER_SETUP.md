# RENDER ENVIRONMENT VARIABLES SETUP GUIDE

## Step-by-Step Instructions

### 1. Go to Render Dashboard
Visit: https://dashboard.render.com/

### 2. Select Your Service
Click on: `ai-website-lzcx` (or your web service name)

### 3. Go to Environment Tab
Click on the "Environment" tab in the left sidebar

### 4. Add These Environment Variables

Click "Add Environment Variable" for each:

**DATABASE_URL** (REQUIRED - This makes signup work!)
```
Key: DATABASE_URL
Value: postgresql://xgenai_db_user:F6x7ohdE2KZ5LMHPfJzQ9muaDkTJY2eC@dpg-d4laq0je5dus73fm14c0-a/xgenai_db
```

**FLASK_ENV** (REQUIRED)
```
Key: FLASK_ENV
Value: production
```

**ADMIN_EMAIL** (Optional - default is admin@xgenai.com)
```
Key: ADMIN_EMAIL
Value: admin@xgenai.com
```

**ADMIN_PASSWORD** (Optional - default is Admin@123)
```
Key: ADMIN_PASSWORD
Value: Admin@123
```

### 5. Save Changes
Click "Save Changes" button

### 6. Manual Deploy
- Click "Manual Deploy" button
- Select "Clear build cache & deploy"
- Wait 2-3 minutes for deployment

### 7. Verify It Works
Test these URLs after deployment:
- Health: https://ai-website-lzcx.onrender.com/health
- Signup: https://ai-website-lzcx.onrender.com/signup
- Admin: https://ai-website-lzcx.onrender.com/xgenai-admin-portal

## What This Does
✅ Connects to PostgreSQL (permanent storage)
✅ All signups are saved forever
✅ Data persists across restarts
✅ Users appear in admin dashboard
✅ Production-ready configuration

## Check Render Logs
After deploying, check logs for:
```
✅ Using PostgreSQL database
✅ PostgreSQL connected successfully
✅ Database initialized successfully
```

If you see these, everything is working!
