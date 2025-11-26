# 🔐 ADMIN QUICK REFERENCE

## Admin Access

**Login URL**: `https://your-site.onrender.com/admin/login`

**Default Credentials**:
```
Email: admin@xgenai.com
Password: Admin@123
```

**⚠️ CHANGE PASSWORD IMMEDIATELY!**

## How to Change Admin Password

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your web service
3. Click "Environment" tab
4. Find `ADMIN_PASSWORD`
5. Update to your new password
6. Click "Save Changes"
7. Wait for auto-redeploy (~2 mins)
8. Login with new password

## URL Structure

All pages work WITHOUT `.html`:

```
✅ /                  → Home
✅ /careers           → Careers page
✅ /auth              → Login/Signup
✅ /apply             → Job application
✅ /admin/login       → Admin login
✅ /admin             → Admin dashboard (protected)
```

## Admin Dashboard Features

After logging in at `/admin/login`:

### 1. View Job Applications
- See all candidates
- Grouped by position
- Full applicant details

### 2. Update Application Status
Choose from:
- ⏳ Pending
- ✉️ Application Received
- 🔍 Under Review
- 🎯 Interview
- ✅ Selected
- ❌ Rejected

### 3. Send Emails
- Click "Send Email" button
- Automated templates for each status
- Notifies candidates instantly

### 4. View Statistics
- Total users
- Emails sent
- Recent activity

## Security Notes

✅ Admin pages are protected  
✅ Must login to access dashboard  
✅ Token expires on logout  
✅ Auto-redirect if not authenticated  

## Logout

Click "Logout" button in navigation menu

## Troubleshooting

**Can't access admin page?**
→ Login at `/admin/login` first

**Forgot password?**
→ Update ADMIN_PASSWORD in Render environment variables

**"Unauthorized" error?**
→ Clear cookies and login again

**Applications not showing?**
→ Check Render logs for backend errors

## Important Files

- `backend.py` - Server logic
- `admin.html` - Dashboard interface
- `admin-login.html` - Login page

## Quick Deploy Commands

```bash
# Local testing
python backend.py

# Check if running
curl http://localhost:5000/

# Test admin login
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@xgenai.com","password":"Admin@123"}'
```

## Environment Variables to Set

```env
ADMIN_EMAIL=admin@xgenai.com
ADMIN_PASSWORD=YourStrongPassword
SECRET_KEY=random-secret-key
DATABASE_URL=<auto-provided>
MAILGUN_API_KEY=your-key
MAILGUN_DOMAIN=yourdomain.com
```

---

**Need Help?** Check `PRODUCTION_READY.md` for detailed documentation
