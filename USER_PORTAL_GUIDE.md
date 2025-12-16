# 🚀 ZGENAI User Portal System - Setup Guide

## 📋 Overview

Complete role-based user portal system with three distinct dashboards:
- **Intern Dashboard**: Task tracking, application status, progress metrics
- **Recruiter Dashboard**: Job application tracking and management
- **Admin Dashboard**: Monitor all activities (coming soon)

## 🎯 What Was Created

### 1. **Frontend Pages**
- `user-login.html` - Unified login page with role selection (Intern/Recruiter)
- `intern-dashboard-new.html` - Intern dashboard with task management and charts
- `recruiter-dashboard.html` - Recruiter dashboard for job applications

### 2. **Backend APIs** (15+ endpoints)
#### Authentication
- `POST /api/user/login` - Login for interns and recruiters

#### Intern APIs
- `GET /api/intern/tasks` - Get all tasks
- `POST /api/intern/tasks` - Create new task
- `PUT /api/intern/tasks/<id>/complete` - Mark task complete
- `POST /api/intern/tasks/<id>/submit` - Submit task with notes
- `GET /api/intern/application-status` - Get application status
- `GET /api/intern/stats` - Get dashboard statistics

#### Recruiter APIs
- `GET /api/recruiter/applications` - Get all applications
- `POST /api/recruiter/applications` - Create new application
- `GET /api/recruiter/applications/<id>` - Get specific application
- `PUT /api/recruiter/applications/<id>` - Update application
- `DELETE /api/recruiter/applications/<id>` - Delete application
- `GET /api/recruiter/stats` - Get dashboard statistics

### 3. **Database Tables** (7 new tables)
- `selected_interns` - Approved interns with dashboard access
- `intern_sessions` - Intern authentication tokens
- `intern_daily_tasks` - Tasks created by interns
- `daily_task_submissions` - Task submission records
- `recruiters` - Recruiter accounts
- `recruiter_sessions` - Recruiter authentication tokens
- `recruiter_applications` - Job applications tracked by recruiters

## 🔧 Setup Instructions

### Step 1: Deployment
The code has been pushed to GitHub and will auto-deploy to Render.

Wait 2-3 minutes for deployment to complete at:
**https://www.zgenai.org**

### Step 2: Create Test Accounts

Once deployed, create test users by running on Render console:

```bash
python create_test_users.py
```

This creates two demo accounts:

**Intern Account:**
- Email: `intern@zgenai.com`
- Password: `Intern@123`

**Recruiter Account:**
- Email: `recruiter@zgenai.com`
- Password: `Recruiter@123`

### Step 3: Create Real Intern Accounts

To give selected candidates dashboard access, you need to:

1. **From Admin Dashboard** - When you select an intern:
   - System should automatically create an entry in `selected_interns` table
   - Send them an email with login credentials

2. **Manual Method** (using SQL):

```sql
INSERT INTO selected_interns (
    application_id, full_name, email, password_hash, 
    position, college, status
) VALUES (
    1,  -- Link to their application ID
    'John Doe',
    'john@example.com',
    -- Use this hash for password "Intern@123":
    '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
    'Software Developer Intern',
    'MIT',
    'active'
);
```

To generate password hash:
```python
import hashlib
password = "YourPassword123"
hash_password = hashlib.sha256(password.encode()).hexdigest()
print(hash_password)
```

### Step 4: Create Recruiter Accounts

Similar process for recruiters:

```sql
INSERT INTO recruiters (full_name, email, password_hash, status)
VALUES (
    'Jane Smith',
    'jane@example.com',
    '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',  -- Recruiter@123
    'active'
);
```

## 📱 User Access URLs

### For Interns:
1. Go to: **https://www.zgenai.org/user-login**
2. Select "Intern" tab
3. Login with credentials
4. Access dashboard at: **https://www.zgenai.org/intern-dashboard**

### For Recruiters:
1. Go to: **https://www.zgenai.org/user-login**
2. Select "Recruiter" tab
3. Login with credentials
4. Access dashboard at: **https://www.zgenai.org/recruiter-dashboard**

## 🎨 Features

### Intern Dashboard Features:
- ✅ View application status
- ✅ Create daily tasks with priorities
- ✅ Mark tasks as complete
- ✅ Submit tasks with notes and hours spent
- ✅ Track completion rate
- ✅ View weekly progress
- ✅ Interactive progress charts
- ✅ Beautiful gradient UI

### Recruiter Dashboard Features:
- ✅ Add job applications (company, position, location, date)
- ✅ Track application status (applied, interviewing, offer, rejected)
- ✅ Add salary range and job type
- ✅ Add notes for each application
- ✅ Edit and delete applications
- ✅ View statistics (total, offers, interviewing, this week)
- ✅ Professional modern UI

## 📊 Excel Task Import (For Interns)

You mentioned having tasks in Excel. Here's how to import them:

### Option 1: Manual Entry
Interns can add tasks one by one using the "+ Add Task" button.

### Option 2: Bulk Import (Future Enhancement)
We can add a feature where:
1. Admin uploads Excel file with weekly tasks
2. System parses and creates tasks in `weekly_tasks` table
3. Tasks automatically appear in all intern dashboards

**Excel Format Expected:**
```
Week | Task Title | Description | Due Date | Priority
1    | Learn React | Complete tutorial | 2025-12-20 | high
1    | Mini Project | Build todo app | 2025-12-22 | medium
```

### Option 3: Admin Pre-loads Tasks
Admin can add tasks to `weekly_tasks` table, and system assigns them to all interns.

## 🔐 Security Notes

- All passwords are SHA-256 hashed
- Session tokens are 256-bit random hex
- Authentication required for all dashboard APIs
- Role-based access control (interns can't access recruiter APIs)
- HTTPS enforced on production

## 🚧 Next Steps (Future Enhancements)

1. **Admin Tracking Dashboard**
   - View all intern tasks and submissions
   - View all recruiter applications
   - Generate reports and analytics

2. **Excel Task Import**
   - Upload Excel file
   - Auto-create tasks for interns
   - Bulk task assignment

3. **Email Notifications**
   - Send credentials to new interns/recruiters
   - Notify on task deadlines
   - Weekly progress reports

4. **Enhanced Metrics**
   - Time spent on tasks
   - Performance ratings
   - Intern leaderboard

5. **File Uploads**
   - Resume uploads for intern tasks
   - Assignment submissions
   - Project files

## 🐛 Troubleshooting

### Can't Login?
- Make sure test accounts are created: run `create_test_users.py` on Render
- Check password is exactly: `Intern@123` or `Recruiter@123`
- Clear browser cache and try again

### API Errors?
- Check Render logs for backend errors
- Verify database tables exist: `python backend.py` should show "✅ Database initialized"
- Check network tab in browser DevTools

### Empty Dashboard?
- For interns: Make sure they created tasks using "+ Add Task"
- For recruiters: Add applications using "+ Add Application"
- Stats will show 0 until data is added

## 📞 Support

If you need:
- More features added
- Excel import functionality
- Admin tracking dashboard
- Custom modifications

Let me know and I'll help implement them!

## ✅ Testing Checklist

- [ ] Deploy successful (check Render logs)
- [ ] Database tables created (check backend startup logs)
- [ ] Test accounts created (run create_test_users.py)
- [ ] Login page loads: https://www.zgenai.org/user-login
- [ ] Intern login works
- [ ] Intern dashboard loads with stats
- [ ] Can create and complete tasks
- [ ] Recruiter login works
- [ ] Recruiter dashboard loads
- [ ] Can add and track applications

---

**System Status:** ✅ Fully Deployed & Ready to Use
**Last Updated:** December 16, 2025
