# XGENAI Deployment Guide 🚀

## Quick Start: Deploy to Render.com (Free)

### Prerequisites
- GitHub account
- Render.com account (sign up free at https://render.com)

### Step 1: Push Code to GitHub

1. Initialize git repository (if not already done):
```powershell
cd "c:\Users\vsaravan\OneDrive - Cadence Design Systems Inc\Desktop\AI-website"
git init
git add .
git commit -m "Initial commit - XGENAI platform"
```

2. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name: `xgenai-platform`
   - Keep it Public
   - Don't initialize with README
   - Click "Create repository"

3. Push code to GitHub:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/xgenai-platform.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. Go to https://render.com and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `xgenai-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend:app`
   - **Instance Type**: `Free`

5. Add Environment Variables (click "Advanced"):
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key-here-generate-random-string
   DATABASE_URL=sqlite:///aisolutions.db
   CORS_ORIGINS=*
   ```

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. Copy your backend URL (e.g., `https://xgenai-backend.onrender.com`)

### Step 3: Deploy Frontend to Vercel/Netlify

#### Option A: Vercel (Recommended)

1. Install Vercel CLI:
```powershell
npm install -g vercel
```

2. Deploy:
```powershell
cd "c:\Users\vsaravan\OneDrive - Cadence Design Systems Inc\Desktop\AI-website"
vercel
```

3. Follow prompts:
   - Login/Sign up
   - Set up and deploy: Yes
   - Which scope: Your username
   - Link to existing project: No
   - Project name: xgenai
   - Directory: ./
   - Overwrite settings: No

4. Update API URLs in your JS files to use Render backend URL

#### Option B: Netlify

1. Go to https://app.netlify.com
2. Drag and drop your AI-website folder
3. Site will be deployed instantly

### Step 4: Update API URLs

Update these files with your Render backend URL:

**dashboard.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

**admin-enhanced.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

**auth-backend.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

**admin-backend.js**:
```javascript
const API_URL = 'https://xgenai-backend.onrender.com';
```

Then commit and push changes:
```powershell
git add .
git commit -m "Update API URLs for production"
git push
```

### Step 5: Test Your Live Site

1. Visit your Vercel/Netlify URL
2. Create an account at `/auth.html`
3. Login and access dashboard at `/dashboard.html`
4. Admin can view all users at `/admin-enhanced.html`

---

## Alternative: Deploy to Heroku

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Deploy
```powershell
heroku login
heroku create xgenai-platform
git push heroku main
heroku open
```

### Step 3: Set Environment Variables
```powershell
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
```

---

## Database Options

### Development (Current)
- SQLite file (`aisolutions.db`)
- Perfect for testing
- Data persists locally

### Production Options

#### 1. PostgreSQL on Render (Free)
1. In Render Dashboard → **"New +"** → **"PostgreSQL"**
2. Name: `xgenai-db`
3. Copy the **Internal Database URL**
4. Add to Web Service environment variables:
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   ```

#### 2. MongoDB Atlas (Free)
1. Sign up at https://cloud.mongodb.com
2. Create free cluster
3. Get connection string
4. Update backend.py to use MongoDB

---

## Post-Deployment Checklist

- [ ] Backend is live and accessible
- [ ] Frontend is live and accessible
- [ ] API URLs updated in all JS files
- [ ] Users can sign up
- [ ] Users can login
- [ ] Dashboard loads correctly
- [ ] Projects can be created
- [ ] Admin dashboard shows all users
- [ ] Email notifications configured (optional)

---

## Monitoring & Maintenance

### Free Monitoring Tools
- **Render**: Built-in logs and metrics
- **UptimeRobot**: Free uptime monitoring (https://uptimerobot.com)
- **Better Stack**: Free log management

### Database Backups
- Render provides automatic PostgreSQL backups
- For SQLite: Download file periodically from Render dashboard

---

## Cost Summary

### Free Tier (Good for MVP)
- Render Backend: Free (750 hours/month)
- Vercel Frontend: Free (100GB bandwidth)
- Total: **$0/month**

### Scaling Options
- Render Starter: $7/month (better performance)
- Vercel Pro: $20/month (custom domain, more bandwidth)
- PostgreSQL: $7/month (persistent DB)

---

## Custom Domain Setup

### After Deployment:
1. Buy domain (Namecheap, GoDaddy, etc.)
2. In Vercel/Netlify:
   - Settings → Domains
   - Add your domain
3. Update DNS records as shown
4. SSL certificate auto-generated

Example: `www.xgenai.com`

---

## Troubleshooting

### Backend Won't Start
- Check logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Check environment variables

### CORS Errors
- Update `CORS_ORIGINS` in backend env variables
- Add your frontend domain

### Database Connection Failed
- Check `DATABASE_URL` format
- Verify database is running
- Check firewall rules

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/

---

## Next Steps

1. **Custom Branding**: Update logo, colors, favicon
2. **Email Setup**: Configure Gmail SMTP for real emails
3. **Analytics**: Add Google Analytics
4. **SEO**: Add meta tags, sitemap
5. **Security**: Add rate limiting, input validation
6. **Features**: Add password reset, profile editing

---

**Your XGENAI platform is now live and accessible to everyone! 🎉**
