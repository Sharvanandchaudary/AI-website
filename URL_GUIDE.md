# Production-Ready URL Structure

## 🔒 Secure Admin Portal (New)

**IMPORTANT**: The admin portal is now at a secure, non-obvious URL to prevent unauthorized access attempts.

### Admin Access URLs:
- **Authentication Portal**: `/xgen-admin-portal`
  - Secure login page with email/password
  - SHA-256 encrypted authentication
  - Token-based session management
  
- **Admin Dashboard**: `/xgen-admin-dashboard`
  - Requires valid authentication token
  - Auto-redirects to login if not authenticated
  - Full access to applications, interns, tasks, users, emails

### Credentials:
```
Email: admin@xgenai.com
Password: Admin@123
```

---

## 🌐 Public URLs (No .html Extension)

### Main Pages:
- **Homepage**: `/` or `/index`
- **Careers**: `/careers`
- **Login/Signup**: `/auth`
- **User Dashboard**: `/dashboard`
- **Job Application**: `/apply`

### Intern Portal:
- **Intern Login**: `/intern-login`
- **Intern Dashboard**: `/intern-dashboard`

---

## 🛡️ Security Features Implemented

### 1. **Secure Admin URLs**
- ❌ Removed: `/admin` (too obvious, security risk)
- ✅ New: `/xgen-admin-portal` (non-obvious, secure)
- ✅ Separate authentication and dashboard pages
- ✅ No redirect loops

### 2. **Cache-Busting**
- Version-based cache control (`CACHE_VERSION = 'v2.1.0'`)
- Unique filenames for admin pages
- No-cache headers for all HTML/CSS/JS
- 1-hour cache for static assets (images)

### 3. **Production Security Headers**
```python
X-Frame-Options: DENY                    # Prevent clickjacking
X-Content-Type-Options: nosniff          # Prevent MIME sniffing
X-XSS-Protection: 1; mode=block          # XSS protection
Strict-Transport-Security: max-age=31536000  # Force HTTPS
Cache-Control: no-cache, no-store        # Prevent sensitive data caching
```

### 4. **Authentication Flow**
```
User visits /xgen-admin-portal
  ↓
Enters credentials
  ↓
POST to /api/admin/login
  ↓
Receives JWT token
  ↓
Token stored in localStorage
  ↓
Redirected to /xgen-admin-dashboard
  ↓
Dashboard checks for token
  ↓
If no token → redirect to /xgen-admin-portal
If valid token → load dashboard data
```

---

## 📋 API Endpoints

### Public APIs:
```
POST /api/signup            - User registration
POST /api/login             - User login
POST /api/applications      - Submit job application
```

### Admin APIs (Auth Required):
```
POST /api/admin/login              - Admin login
GET  /api/stats                    - Dashboard statistics
GET  /api/users                    - All users
GET  /api/emails                   - Email history
GET  /api/admin/applications       - All applications
POST /api/admin/select-intern      - Select applicant as intern
GET  /api/admin/interns            - All interns
POST /api/admin/weekly-task        - Create task
```

### Intern APIs (Auth Required):
```
POST /api/intern/login       - Intern login
GET  /api/intern/dashboard   - Get tasks and progress
POST /api/intern/submit-task - Submit task work
```

---

## 🚀 Production Deployment

### Current Status:
✅ Deployed on Render.com
✅ PostgreSQL database configured
✅ HTTPS/SSL enabled
✅ Auto-deploy from GitHub main branch
✅ Security headers active
✅ Cache-busting implemented

### Deployment URL:
```
https://xgenai.onrender.com
```

### Admin Portal Access:
```
https://xgenai.onrender.com/xgen-admin-portal
```

---

## 🔄 Migration from Old URLs

### Old URLs (Deprecated):
- ❌ `/admin` → Security risk, removed
- ❌ `/admin-login.html` → Had cache issues
- ❌ `/admin-v3.html` → Confusing redirect logic
- ❌ `/careers.html` → Use `/careers` instead
- ❌ `/auth.html` → Use `/auth` instead

### New URLs (Active):
- ✅ `/xgen-admin-portal` → Admin login
- ✅ `/xgen-admin-dashboard` → Admin dashboard
- ✅ `/careers` → Job listings
- ✅ `/auth` → User login/signup
- ✅ `/apply` → Application form
- ✅ `/intern-login` → Intern login
- ✅ `/intern-dashboard` → Intern portal

---

## 📱 Testing Guide

### 1. Test Admin Authentication:
```bash
# Visit admin portal
curl https://xgenai.onrender.com/xgen-admin-portal

# Login API
curl -X POST https://xgenai.onrender.com/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@xgenai.com","password":"Admin@123"}'
```

### 2. Test Clean URLs:
```bash
# Should work without .html
curl https://xgenai.onrender.com/careers
curl https://xgenai.onrender.com/auth
curl https://xgenai.onrender.com/apply
```

### 3. Test Security Headers:
```bash
curl -I https://xgenai.onrender.com/xgen-admin-portal | grep -E "X-Frame|X-Content|Strict-Transport"
```

---

## 📊 Browser Cache Bypass

If you're still seeing old admin pages:

### Chrome/Edge:
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Or: `Ctrl + F5` for hard refresh

### Firefox:
1. Press `Ctrl + Shift + Delete`
2. Select "Cache"
3. Click "Clear Now"
4. Or: `Ctrl + Shift + R` for hard refresh

### Best Solution:
Use the new URL directly: `/xgen-admin-portal`

---

## 🔐 Security Best Practices

### For Production:
1. ✅ Never share admin URL publicly
2. ✅ Use HTTPS only (no HTTP)
3. ✅ Rotate passwords regularly
4. ✅ Monitor login attempts
5. ✅ Use strong passwords (min 12 chars)
6. ✅ Enable 2FA (future enhancement)
7. ✅ Regular security audits
8. ✅ Keep dependencies updated

### Environment Variables:
```bash
# Never commit these to Git
DATABASE_URL=postgresql://...
SECRET_KEY=...
MAILGUN_API_KEY=...
```

---

## 📝 Notes

- All old admin URLs are removed for security
- New URLs are production-ready and enterprise-grade
- Cache issues resolved with versioning and unique filenames
- Security headers prevent common web vulnerabilities
- Clean URLs improve SEO and user experience
- Separate auth/dashboard pages prevent redirect loops

---

**Last Updated**: November 29, 2025
**Version**: 2.1.0
**Status**: Production Ready ✅
