# 🚀 XGENAI Production Setup - Quick Commands

## Prerequisites
- GitHub account
- Render.com account (https://render.com)
- Netlify account (https://netlify.com)
- Mailgun account (https://mailgun.com)

---

## 1️⃣ Push to GitHub (5 minutes)

```powershell
# Navigate to project
cd "c:\Users\vsaravan\OneDrive - Cadence Design Systems Inc\Desktop\AI-website"

# Initialize Git
git init
git add .
git commit -m "XGENAI platform - initial deploy"

# Create repo on github.com/new
# Name: xgenai-platform
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/xgenai-platform.git
git branch -M main
git push -u origin main
```

✅ **Verify**: Check github.com - your code should be there

---

## 2️⃣ Setup Mailgun (3 minutes)

1. Go to https://mailgun.com → Sign up
2. **For testing**: Use sandbox domain (free, pre-configured)
3. **Settings → API Keys** → Copy "Private API key"
4. **Sending → Domains** → Copy sandbox domain
5. **Add authorized recipients** (emails you want to test with)

**Save these**:
```
MAILGUN_API_KEY: key-xxxxxxxxxxxxx
MAILGUN_DOMAIN: sandboxXXXXXX.mailgun.org
MAILGUN_FROM_EMAIL: noreply@sandboxXXXXXX.mailgun.org
```

---

## 3️⃣ Deploy Backend to Render (7 minutes)

### Create PostgreSQL Database:
1. https://render.com → **New +** → **PostgreSQL**
2. Name: `xgenai-db`
3. Database: `xgenai`
4. User: `xgenai`
5. Region: Oregon (Free)
6. Plan: **Starter** ($7/mo) or **Free**
7. Click **Create Database**
8. Copy **Internal Database URL**

### Create Web Service:
1. **New +** → **Web Service**
2. **Connect GitHub** → Select `xgenai-platform`
3. Configure:
   - Name: `xgenai-backend`
   - Environment: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn backend:app`
   - Plan: **Starter** ($7/mo) - recommended (no sleep)

4. **Environment Variables** (click Advanced):
```
FLASK_ENV=production
SECRET_KEY=xgenai-secret-2025-production-key-change-this
DATABASE_URL=<paste-your-postgresql-internal-url>
CORS_ORIGINS=*
MAILGUN_API_KEY=<your-mailgun-key>
MAILGUN_DOMAIN=<your-mailgun-domain>
MAILGUN_FROM_EMAIL=noreply@<your-mailgun-domain>
```

5. Click **Create Web Service**

6. Wait 5-10 minutes for deployment

7. **Copy backend URL**: `https://xgenai-backend.onrender.com`

✅ **Test**: Visit `https://xgenai-backend.onrender.com/api/stats`
Should return JSON with stats

---

## 4️⃣ Deploy Frontend to Netlify (2 minutes)

### Option A: Drag & Drop (Fastest)
1. Go to https://app.netlify.com
2. Drag the `AI-website` folder
3. Done! Copy the URL

### Option B: GitHub (Recommended)
1. **Add new site** → **Import from Git**
2. Connect **GitHub** → Select `xgenai-platform`
3. Settings:
   - Build command: (leave empty)
   - Publish directory: `.`
4. Click **Deploy**

5. **Copy your URL**: `https://sparkling-cupcake-abc123.netlify.app`

---

## 5️⃣ Update Frontend with Backend URL (2 minutes)

Update these 4 files on your computer:

### auth-backend.js (line 2):
```javascript
const API_URL = 'https://xgenai-backend.onrender.com/api';
```

### dashboard.js (line 1):
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

### admin-enhanced.js (line 1):
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

### admin-backend.js (line 2):
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

### Push changes:
```powershell
git add .
git commit -m "Update API URLs for production"
git push
```

Netlify will auto-redeploy in 30 seconds!

---

## 6️⃣ Update Render CORS (1 minute)

1. Go to Render Web Service
2. **Environment** tab
3. Update `CORS_ORIGINS`:
```
https://your-actual-netlify-url.netlify.app
```
4. **Save Changes** (auto-restarts)

---

## ✅ Test Your Live Site

1. Visit: `https://your-site.netlify.app`
2. Click **Login/Signup**
3. Create account → Check email (Mailgun)
4. Login → See dashboard
5. Add project → Saves to PostgreSQL
6. Visit `/admin-enhanced.html` → See all users

---

## 🎉 Your Site is LIVE!

**Frontend**: https://your-site.netlify.app
**Backend**: https://xgenai-backend.onrender.com
**Database**: PostgreSQL on Render
**Emails**: Mailgun

**Share your URL with anyone worldwide!**

---

## 💰 Cost: $14/month

- **Render Starter**: $7/month (backend always on)
- **PostgreSQL Starter**: $7/month (persistent DB)
- **Netlify**: FREE
- **Mailgun**: FREE (5,000 emails/month)

**Alternative - FREE tier** (backend sleeps after 15min):
- Everything FREE but slower first load

---

## 🔧 Quick Fixes

### Backend URL not working?
```powershell
# Visit your Render dashboard → Logs
# Check for errors
```

### CORS error?
```
Update CORS_ORIGINS in Render with your exact Netlify URL
Include https:// and no trailing slash
```

### Email not sending?
```
Check Mailgun dashboard → Sending → Logs
Verify API key and domain are correct
For sandbox: add recipient to authorized list
```

---

## 📱 Custom Domain (Optional)

### Buy domain: 
- Namecheap.com or Google Domains ($12/year)

### Setup:
1. **Netlify**: Site settings → Domain → Add custom domain
2. **Update DNS** as shown by Netlify
3. **SSL auto-configured** by Netlify

Your site: `https://www.xgenai.com` 🎉

---

## Need Help?

Check:
1. Render Logs (for backend errors)
2. Browser Console F12 (for frontend errors)
3. Mailgun Logs (for email issues)

**Everything working? Share your site URL!** 🚀
