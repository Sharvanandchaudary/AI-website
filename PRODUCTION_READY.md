# XGENAI Website - Production Ready Setup

## 🎉 What's Been Implemented

### 1. Clean URL Routing (No .html extensions)
- All pages now accessible without `.html` extension
- Example: `/careers` instead of `/careers.html`
- Flask handles routing for clean URLs

### 2. Secure Admin System
- **Admin Login Page**: `/admin/login`
- **Protected Dashboard**: `/admin` (requires authentication)
- Token-based session management
- Auto-redirect to login if not authenticated
- Secure logout functionality

### 3. Default Admin Credentials
```
Email: admin@xgenai.com
Password: Admin@123
```
**⚠️ IMPORTANT: Change these immediately in production!**

## 📁 File Changes Summary

### Backend (`backend.py`)
- ✅ Added clean URL routes for all pages
- ✅ Implemented admin authentication system
- ✅ Added `/api/admin/login` endpoint
- ✅ Added `/api/admin/logout` endpoint
- ✅ Protected all admin API endpoints with token verification
- ✅ Admin session management with secure tokens

### Frontend Updates

#### New File: `admin-login.html`
- Professional admin login interface
- Token management (cookies + localStorage)
- Auto-redirect if already logged in
- Error handling and validation

#### Updated: `admin.html`
- ✅ Authentication check on page load
- ✅ Auto-redirect to login if not authenticated
- ✅ Logout button added to navigation
- ✅ All API calls include authentication token
- ✅ 401 responses trigger logout

#### Updated Navigation (All Pages)
Files updated with clean URLs:
- `index.html` - Home page
- `careers.html` - Careers page
- `auth.html` - Login/Signup page
- `admin.html` - Admin dashboard
- `dashboard.html` - User dashboard
- `pages/apply.html` - Application form

## 🔒 Security Features

1. **Token-Based Authentication**
   - Secure 32-byte URL-safe tokens
   - Stored in both cookies and localStorage
   - Sent with every admin API request

2. **Protected Endpoints**
   - `/api/admin/applications` - View job applications
   - `/api/admin/applications/<id>/status` - Update status
   - `/api/admin/send-application-email` - Send emails
   - All return 401 if token invalid

3. **Session Management**
   - In-memory session storage
   - Automatic logout on invalid token
   - Manual logout clears all tokens

## 🚀 How to Deploy on Render

### Step 1: Environment Variables
Add these to your Render web service:

```env
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-generate-new-one
ADMIN_EMAIL=admin@xgenai.com
ADMIN_PASSWORD=YourStrongPassword123!
DATABASE_URL=<auto-provided-by-render>
MAILGUN_API_KEY=your-mailgun-key
MAILGUN_DOMAIN=yourdomain.com
MAILGUN_FROM_EMAIL=noreply@yourdomain.com
CORS_ORIGINS=https://your-site.onrender.com
```

### Step 2: Build Settings on Render
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn backend:app
```

### Step 3: Add PostgreSQL Database
- Create PostgreSQL database on Render
- Link it to your web service
- DATABASE_URL will be auto-populated

### Step 4: Deploy
- Push code to GitHub
- Render will auto-deploy
- Check logs for any errors

## 🌐 URLs After Deployment

| Feature | URL | Auth Required |
|---------|-----|---------------|
| Home | `/` | No |
| Careers | `/careers` | No |
| Login/Signup | `/auth` | No |
| Apply to Job | `/apply` | No |
| **Admin Login** | `/admin/login` | No |
| **Admin Dashboard** | `/admin` | **Yes** |
| User Dashboard | `/dashboard` | Yes (user) |

## 🔐 Admin Login Flow

1. User visits `/admin`
2. Page checks for authentication token
3. If no token → redirect to `/admin/login`
4. User enters credentials at login page
5. Backend validates credentials
6. If valid → token generated and stored
7. User redirected to `/admin` dashboard
8. All admin API calls include token
9. Logout clears token and redirects to login

## 🧪 Testing Locally

```bash
# 1. Install dependencies
pip install flask flask-cors python-dotenv psycopg2-binary requests gunicorn

# 2. Create .env file
echo "FLASK_ENV=development
SECRET_KEY=dev-secret-key
ADMIN_EMAIL=admin@xgenai.com
ADMIN_PASSWORD=Admin@123
DATABASE_URL=aisolutions.db" > .env

# 3. Run server
python backend.py

# 4. Test URLs
# Home: http://localhost:5000/
# Careers: http://localhost:5000/careers
# Admin Login: http://localhost:5000/admin/login
# Admin Dashboard: http://localhost:5000/admin
```

## ✅ Testing Checklist

After deployment, test these:

- [ ] Home page loads at `/`
- [ ] Careers page loads at `/careers`
- [ ] Can submit job application
- [ ] Admin login page loads at `/admin/login`
- [ ] Can login with admin credentials
- [ ] Admin dashboard loads after login
- [ ] Can view job applications in admin
- [ ] Can update application status
- [ ] Can send emails to applicants
- [ ] Logout works and redirects to login
- [ ] Accessing `/admin` without login redirects to `/admin/login`
- [ ] All navigation links work without .html

## 🔄 To Change Admin Password

### Method 1: Environment Variable (Recommended)
1. Go to Render Dashboard
2. Navigate to your web service
3. Go to "Environment" tab
4. Update `ADMIN_PASSWORD` variable
5. Click "Save Changes"
6. Service will auto-redeploy

### Method 2: For Multiple Admins (Future)
Edit `backend.py`:
```python
ADMIN_USERS = {
    'admin@xgenai.com': {
        'password_hash': hashlib.sha256('NewPassword123!'.encode()).hexdigest(),
        'role': 'admin'
    },
    'manager@xgenai.com': {
        'password_hash': hashlib.sha256('ManagerPass456!'.encode()).hexdigest(),
        'role': 'admin'
    }
}
```

## 📊 Admin Dashboard Features

Once logged in, admins can:
- View all job applications grouped by position
- See applicant details (name, email, college, etc.)
- Update application status (6 states available)
- Send status notification emails to candidates
- View user registrations
- Monitor email history
- Real-time statistics

## 🐛 Troubleshooting

### "Unauthorized" Error on Admin Page
**Fix**: Clear browser cookies and localStorage, then login again

### Admin Page Shows Login Page
**Fix**: This is normal if not logged in. Login at `/admin/login`

### Can't Access `/admin` After Login
**Fix**: Check browser console for errors. Ensure cookies are enabled.

### Backend Not Responding
**Fix**: Check Render logs. Verify all environment variables are set.

## 🎯 Next Steps (Optional Enhancements)

1. **Add password reset functionality**
2. **Implement 2FA for admin**
3. **Add rate limiting on login attempts**
4. **Store admin users in database instead of hardcoding**
5. **Add admin activity logs**
6. **Implement role-based permissions (admin, manager, viewer)**
7. **Add session timeout (auto-logout after inactivity)**
8. **Email verification for new admins**

## 📝 Important Notes

1. **Change default admin password immediately after first deployment**
2. **Keep SECRET_KEY secret and unique per environment**
3. **Use HTTPS in production (Render provides this automatically)**
4. **Regularly backup your PostgreSQL database**
5. **Monitor Render logs for suspicious login attempts**
6. **Test all features after deployment**

## 💡 Key Improvements Made

**Before:**
- ❌ URLs had .html extensions (`/careers.html`)
- ❌ Admin page was publicly accessible
- ❌ No authentication system
- ❌ Anyone could access admin APIs

**After:**
- ✅ Clean URLs (`/careers`)
- ✅ Protected admin area with login
- ✅ Token-based authentication
- ✅ Secure API endpoints
- ✅ Professional admin interface
- ✅ Production-ready deployment

---

## 🆘 Support

If you encounter issues:

1. **Check Render Logs**: Dashboard → Your Service → Logs
2. **Browser Console**: F12 → Console tab for frontend errors
3. **Test Login**: Try admin login with correct credentials
4. **Verify Environment**: Ensure all env variables are set
5. **Database Connection**: Confirm PostgreSQL is linked

## ✨ Success Indicators

Your deployment is successful when:
- ✅ All pages load without .html in URL
- ✅ Admin login page is accessible
- ✅ Can login to admin dashboard
- ✅ Job applications are visible in admin panel
- ✅ Can update statuses and send emails
- ✅ Unauthorized access redirects to login

---

**Version**: 2.0 (Production Ready with Admin Auth)  
**Date**: November 26, 2025  
**Status**: ✅ Ready for Deployment
