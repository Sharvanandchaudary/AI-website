# Production Deployment Guide for XGENAI

## 🚀 Quick Deploy (15 minutes)

### Step 1: Push to GitHub

```powershell
cd "c:\Users\vsaravan\OneDrive - Cadence Design Systems Inc\Desktop\AI-website"

# Initialize git
git init
git add .
git commit -m "Initial commit - XGENAI platform"

# Create repo on GitHub.com (go to github.com/new)
# Name it: xgenai-platform
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/xgenai-platform.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. **Go to https://render.com** and sign up/login

2. **Click "New +" → "Web Service"**

3. **Connect GitHub** → Select `xgenai-platform` repo

4. **Configure**:
   - **Name**: `xgenai-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend:app`
   - **Instance Type**: `Starter` ($7/month) or `Free`

5. **Add Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key-here-use-long-string
   DATABASE_URL=postgresql://user:pass@host/db (Render will provide this)
   CORS_ORIGINS=https://your-netlify-site.netlify.app
   MAILGUN_API_KEY=your-mailgun-api-key
   MAILGUN_DOMAIN=your-mailgun-domain.com
   MAILGUN_FROM_EMAIL=noreply@your-mailgun-domain.com
   ```

6. **Add PostgreSQL Database**:
   - In Render Dashboard → "New +" → "PostgreSQL"
   - Name: `xgenai-db`
   - Plan: `Free` (or `Starter`)
   - Copy **Internal Database URL**
   - Go back to your Web Service
   - Update `DATABASE_URL` environment variable

7. **Click "Create Web Service"** (takes 5-10 minutes)

8. **Copy your backend URL**: `https://xgenai-backend.onrender.com`

### Step 3: Setup Mailgun for Emails

1. **Go to https://mailgun.com** and sign up

2. **Verify your domain** (or use sandbox for testing):
   - Go to **Sending** → **Domains**
   - Click **Add New Domain**
   - Follow DNS setup instructions

3. **Get API Credentials**:
   - Go to **Settings** → **API Keys**
   - Copy your **Private API Key**
   - Your domain: `mg.yourdomain.com` (or sandbox domain)

4. **Update Render Environment Variables**:
   - Go to your Render Web Service
   - **Environment** tab
   - Update:
     - `MAILGUN_API_KEY`: your-private-api-key
     - `MAILGUN_DOMAIN`: mg.yourdomain.com
     - `MAILGUN_FROM_EMAIL`: noreply@mg.yourdomain.com

5. **Test email** (optional):
   - Add authorized recipients in Mailgun (for sandbox)
   - Create an account on your site to test

### Step 4: Deploy Frontend to Netlify

#### Option A: Drag and Drop (Easiest)

1. **Go to https://app.netlify.com**

2. **Drag your `AI-website` folder** onto Netlify

3. **Update API URLs** in your deployed site:
   - Go to **Site settings** → **Build & deploy** → **Environment**
   - Or update locally and redeploy

#### Option B: Git-Based (Recommended)

1. **Go to https://app.netlify.com**

2. **Click "Add new site" → "Import an existing project"**

3. **Connect to GitHub** → Select `xgenai-platform`

4. **Configure**:
   - **Build command**: (leave empty)
   - **Publish directory**: `.`
   - Click **Deploy site**

5. **Copy your site URL**: `https://your-site-name.netlify.app`

### Step 5: Update Frontend API URLs

Update these files with your Render backend URL:

**1. auth-backend.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com/api';
```

**2. dashboard.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

**3. admin-enhanced.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

**4. admin-backend.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

**Then push changes**:
```powershell
git add .
git commit -m "Update API URLs for production"
git push
```

Netlify will auto-deploy in 1 minute!

### Step 6: Update Render CORS

1. Go to your Render Web Service
2. **Environment** tab
3. Update `CORS_ORIGINS`:
   ```
   https://your-actual-site.netlify.app
   ```
4. **Save changes** (service will restart)

---

## ✅ Verify Everything Works

1. **Visit your Netlify site**: `https://your-site.netlify.app`
2. **Create an account** → Should receive email via Mailgun
3. **Login** → Should see dashboard
4. **Add a project** → Should save to PostgreSQL
5. **Check admin panel** → Should see all users

---

## 📝 Environment Variables Checklist

### Render Backend:
- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY=<random-string>`
- [ ] `DATABASE_URL=<postgresql-url-from-render>`
- [ ] `CORS_ORIGINS=<your-netlify-url>`
- [ ] `MAILGUN_API_KEY=<from-mailgun>`
- [ ] `MAILGUN_DOMAIN=<from-mailgun>`
- [ ] `MAILGUN_FROM_EMAIL=<from-mailgun>`

### Netlify Frontend:
- [ ] All JS files updated with Render backend URL
- [ ] `netlify.toml` updated with backend URL

---

## 💰 Cost Summary

### Free Tier:
- **Render Free**: 750 hours/month, sleeps after 15min inactive
- **PostgreSQL Free**: 1GB storage, 97 connections
- **Netlify Free**: 100GB bandwidth, 300 build minutes
- **Mailgun Free**: 5,000 emails/month for 3 months

**Total: $0/month**

### Recommended Paid (No Sleep):
- **Render Starter**: $7/month (always on, better performance)
- **PostgreSQL Starter**: $7/month (persistent, backups)
- **Netlify Pro**: $19/month (custom domain, more bandwidth)
- **Mailgun Flex**: $35/month (50,000 emails)

**Total: $14-68/month depending on needs**

---

## 🔧 Troubleshooting

### Backend not starting:
- Check Render logs: Dashboard → Logs
- Verify all environment variables are set
- Check `requirements.txt` has all dependencies

### CORS errors:
- Update `CORS_ORIGINS` in Render with exact Netlify URL
- Include `https://` prefix
- No trailing slash

### Database connection failed:
- Verify `DATABASE_URL` starts with `postgresql://`
- Check PostgreSQL database is running
- Verify connection string is correct

### Emails not sending:
- Check Mailgun API key is correct
- Verify domain is verified in Mailgun
- Check Mailgun logs in dashboard
- For sandbox: add recipient emails to authorized list

### Frontend can't reach backend:
- Check API URLs in all JS files
- Verify Render service is running
- Check browser console for errors

---

## 🎯 Post-Deployment

### Add Custom Domain:
1. Buy domain (Namecheap, GoDaddy, etc.)
2. **Netlify**:
   - Site settings → Domain management
   - Add custom domain
   - Update DNS records
3. **Mailgun**: Update domain for branded emails

### Monitor Your Site:
- **Render**: Built-in logs and metrics
- **Netlify**: Analytics in dashboard
- **UptimeRobot**: Free uptime monitoring
- **Google Analytics**: Add tracking code

### Backup Database:
- Render Pro: Automatic backups
- Free: Manually export from Render dashboard

---

## 📧 Need Help?

If you see errors:
1. Check Render logs
2. Check browser console (F12)
3. Verify all environment variables
4. Test backend directly: `https://your-backend.onrender.com/api/stats`

---

**Your XGENAI platform is now live worldwide! 🎉**

Share your Netlify URL with anyone to let them access it!
