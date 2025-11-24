# Environment Configuration

## Production Setup

This application can be deployed to production using multiple hosting options.

### Option 1: Render (Backend + Database) - RECOMMENDED

1. **Sign up at https://render.com**
2. **Create New Web Service**
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn backend:app`
   - Environment: Python 3.11

3. **Add Environment Variables**
   ```
   FLASK_ENV=production
   DATABASE_URL=postgresql://... (Render provides this)
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   SECRET_KEY=your-secret-key-here
   ```

4. **Add PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Copy the Internal Database URL
   - Add it to your web service environment variables

### Option 2: Heroku (Backend + Database)

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku login
   heroku create your-app-name
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set MAIL_USERNAME=your-email@gmail.com
   heroku config:set MAIL_PASSWORD=your-app-password
   heroku config:set SECRET_KEY=your-secret-key-here
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: Vercel (Frontend) + Render (Backend)

**Frontend (Vercel):**
1. Sign up at https://vercel.com
2. Import your GitHub repository
3. Deploy static files (HTML, CSS, JS)

**Backend (Render):**
- Follow Render instructions above

### Option 4: AWS (Full Production)

1. **EC2 Instance** - Run backend server
2. **RDS PostgreSQL** - Database
3. **S3 + CloudFront** - Static files
4. **Route 53** - Custom domain

## Database Migration (SQLite to PostgreSQL)

For production, you should migrate from SQLite to PostgreSQL:

1. **Update requirements.txt**
   ```
   psycopg2-binary==2.9.9
   ```

2. **Update backend.py**
   ```python
   import os
   DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///aisolutions.db')
   
   if DATABASE_URL.startswith('postgres://'):
       DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
   ```

## Data Storage in Production

### Development (Local)
- **Database**: `aisolutions.db` (SQLite file)
- **Location**: Project folder
- **Access**: Only on your machine

### Production (Hosted)
- **Database**: PostgreSQL (Cloud)
- **Location**: Render/Heroku/AWS servers
- **Access**: Worldwide via domain name
- **Backup**: Automatic daily backups
- **Persistence**: Data saved permanently
- **Scalability**: Handles thousands of users

## GitHub OAuth Setup

1. **Go to GitHub Settings** → Developer Settings → OAuth Apps
2. **Create New OAuth App**
   - Application name: AI Solutions
   - Homepage URL: https://your-domain.com
   - Authorization callback URL: https://your-domain.com/auth/github/callback

3. **Add to Environment Variables**
   ```
   GITHUB_CLIENT_ID=your-client-id
   GITHUB_CLIENT_SECRET=your-client-secret
   ```

## Custom Domain Setup

1. **Purchase Domain** (Namecheap, GoDaddy, etc.)
2. **Add DNS Records**
   - Type: A
   - Name: @
   - Value: Your server IP / Render URL

3. **Enable HTTPS** (Automatic on Render/Vercel)

## Production URLs

After deployment, your app will be accessible at:

- **Render**: `https://your-app-name.onrender.com`
- **Heroku**: `https://your-app-name.herokuapp.com`
- **Vercel**: `https://your-app-name.vercel.app`
- **Custom Domain**: `https://yourdomain.com`

## Monitoring & Analytics

Add these services:
- **Sentry** - Error tracking
- **Google Analytics** - User analytics
- **Uptime Robot** - Server monitoring

## Cost Estimate

### Free Tier Options:
- **Render**: Free for small apps (spins down after inactivity)
- **Vercel**: Free for personal projects
- **Railway**: $5/month credit

### Paid Options:
- **Render Pro**: $7/month
- **Heroku Hobby**: $7/month
- **AWS**: Pay as you go (~$10-50/month)

## Security in Production

1. **Use HTTPS** (Automatic on most platforms)
2. **Strong SECRET_KEY** (Generate with `secrets.token_hex(32)`)
3. **Environment Variables** (Never commit passwords)
4. **Rate Limiting** (Prevent abuse)
5. **CORS Settings** (Restrict origins)

## Quick Deploy Commands

```bash
# 1. Initialize Git
git init
git add .
git commit -m "Initial commit"

# 2. Create GitHub repository
# Go to github.com and create new repo

# 3. Push to GitHub
git remote add origin https://github.com/yourusername/ai-website.git
git branch -M main
git push -u origin main

# 4. Deploy to Render (auto-deploys from GitHub)
# Just connect your repo on Render dashboard
```

## Support

For deployment issues:
- Render: https://render.com/docs
- Heroku: https://devcenter.heroku.com
- Vercel: https://vercel.com/docs
