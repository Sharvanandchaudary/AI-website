# Google Cloud Platform (GCP) Deployment Guide

Complete guide to deploy the XGenAI application to Google Cloud Platform with PostgreSQL database and automated email exports.

## 📋 Prerequisites

1. **Google Cloud Account**
   - Active GCP account with billing enabled
   - gcloud CLI installed: https://cloud.google.com/sdk/docs/install

2. **Local Tools**
   - Docker Desktop installed
   - Git installed
   - Terminal/Command Line access

3. **GCP Project Setup**
   ```bash
   # Login to GCP
   gcloud auth login
   
   # Create new project (or use existing)
   gcloud projects create xgenai-app --name="XGenAI Application"
   
   # Set project
   gcloud config set project xgenai-app
   
   # Enable required APIs
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     sqladmin.googleapis.com \
     compute.googleapis.com \
     containerregistry.googleapis.com
   ```

## 🗄️ Part 1: Set Up Cloud SQL (PostgreSQL Database)

### Step 1: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create xgenai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_STRONG_PASSWORD \
  --storage-size=10GB \
  --storage-type=SSD \
  --availability-type=zonal

# Wait for instance to be ready (takes 5-10 minutes)
gcloud sql instances list
```

### Step 2: Create Database and User

```bash
# Create database
gcloud sql databases create xgenai \
  --instance=xgenai-db

# Create database user
gcloud sql users create xgenai_user \
  --instance=xgenai-db \
  --password=YOUR_DB_USER_PASSWORD

# Get connection name (save this!)
gcloud sql instances describe xgenai-db --format='value(connectionName)'
# Output example: xgenai-app:us-central1:xgenai-db
```

### Step 3: Configure Database Connection

```bash
# Allow Cloud Run to access Cloud SQL
gcloud sql instances patch xgenai-db \
  --authorized-networks=0.0.0.0/0

# Or use Cloud SQL Proxy (recommended for security)
# The Docker container will use Cloud SQL Proxy automatically
```

## 🐳 Part 2: Build and Push Docker Image

### Step 1: Build Docker Image Locally (Test)

```bash
# Navigate to project directory
cd /path/to/AI-website

# Build image
docker build -t xgenai-app:latest .

# Test locally with docker-compose
docker-compose up
# Access at http://localhost:8080
# Press Ctrl+C to stop

# Clean up test
docker-compose down
```

### Step 2: Configure Docker for GCP

```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Set region
export REGION=us-central1
```

### Step 3: Build and Push to Google Container Registry

```bash
# Build and tag for GCR
docker build -t gcr.io/xgenai-app/xgenai:latest .

# Push to Google Container Registry
docker push gcr.io/xgenai-app/xgenai:latest

# Verify image
gcloud container images list --repository=gcr.io/xgenai-app
```

## ☁️ Part 3: Deploy to Cloud Run

### Step 1: Create Environment Variables

```bash
# Get Cloud SQL connection name
export SQL_CONNECTION_NAME=$(gcloud sql instances describe xgenai-db --format='value(connectionName)')

# Set database URL
export DATABASE_URL="postgresql://xgenai_user:YOUR_DB_USER_PASSWORD@/xgenai?host=/cloudsql/$SQL_CONNECTION_NAME"
```

### Step 2: Deploy to Cloud Run

```bash
# Deploy application
gcloud run deploy xgenai-app \
  --image gcr.io/xgenai-app/xgenai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --add-cloudsql-instances $SQL_CONNECTION_NAME \
  --set-env-vars "DATABASE_URL=$DATABASE_URL,ADMIN_EMAIL=admin@xgenai.com,ADMIN_PASSWORD=Admin@123,PORT=8080,FLASK_ENV=production"

# Get service URL
gcloud run services describe xgenai-app \
  --region us-central1 \
  --format='value(status.url)'
# Save this URL - it's your application URL!
```

### Step 3: Configure Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service xgenai-app \
  --domain your-domain.com \
  --region us-central1

# Follow DNS instructions provided
```

## 📊 Part 4: Set Up Cloud Storage for Exports

### Step 1: Create Storage Bucket

```bash
# Create bucket for email exports
gsutil mb -l us-central1 gs://xgenai-exports

# Set bucket permissions
gsutil iam ch serviceAccount:YOUR_SERVICE_ACCOUNT@xgenai-app.iam.gserviceaccount.com:objectAdmin gs://xgenai-exports
```

### Step 2: Update Application to Use Cloud Storage

Add to your `email_export.py`:

```python
from google.cloud import storage

def upload_to_gcs(local_file, bucket_name='xgenai-exports'):
    """Upload file to Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(local_file))
    blob.upload_from_filename(local_file)
    print(f"✅ Uploaded to GCS: {local_file}")
```

## ⏰ Part 5: Set Up Cloud Scheduler for Cron Jobs

### Step 1: Create Service Account

```bash
# Create service account for scheduler
gcloud iam service-accounts create xgenai-scheduler \
  --display-name="XGenAI Email Export Scheduler"

# Grant permissions
gcloud projects add-iam-policy-binding xgenai-app \
  --member="serviceAccount:xgenai-scheduler@xgenai-app.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Step 2: Create Export Endpoint in Backend

Add to `backend.py`:

```python
@app.route('/cron/export-emails', methods=['POST'])
def cron_export_emails():
    """Endpoint for Cloud Scheduler"""
    # Verify cron header
    if request.headers.get('X-Appengine-Cron') != 'true':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from email_export import main as export_main
        export_main()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Step 3: Create Cloud Scheduler Job

```bash
# Create scheduler job to run daily at 2 AM
gcloud scheduler jobs create http email-export-daily \
  --schedule="0 2 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/cron/export-emails" \
  --http-method=POST \
  --oidc-service-account-email=xgenai-scheduler@xgenai-app.iam.gserviceaccount.com \
  --location=us-central1 \
  --time-zone="America/New_York"

# Test the job manually
gcloud scheduler jobs run email-export-daily --location=us-central1

# View job logs
gcloud scheduler jobs describe email-export-daily --location=us-central1
```

## 🔒 Part 6: Security & Configuration

### Step 1: Set Up Secrets

```bash
# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo -n "YOUR_ADMIN_PASSWORD" | gcloud secrets create admin-password --data-file=-
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding admin-password \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@xgenai-app.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 2: Update Cloud Run with Secrets

```bash
# Redeploy with secrets
gcloud run deploy xgenai-app \
  --image gcr.io/xgenai-app/xgenai:latest \
  --region us-central1 \
  --update-secrets=ADMIN_PASSWORD=admin-password:latest,DB_PASSWORD=db-password:latest
```

## 📈 Part 7: Monitoring & Logging

### Step 1: Enable Monitoring

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=xgenai-app" \
  --limit 50 \
  --format json

# Create log-based metrics
gcloud logging metrics create signup_count \
  --description="Count of user signups" \
  --log-filter='resource.type="cloud_run_revision" AND textPayload=~"User signup successful"'
```

### Step 2: Set Up Alerts

```bash
# Create alert for errors
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="XGenAI High Error Rate" \
  --condition-display-name="Error rate > 10%" \
  --condition-threshold-value=0.1 \
  --condition-threshold-duration=300s
```

## 💰 Part 8: Cost Optimization

### Recommended Configuration

**For Development:**
```bash
--tier=db-f1-micro        # ~$10/month
--memory=512Mi            # Cloud Run
--max-instances=3
```

**For Production:**
```bash
--tier=db-g1-small        # ~$25/month
--memory=1Gi              # Cloud Run
--max-instances=10
--min-instances=1         # Keeps 1 instance warm
```

### Cost Estimates

| Service | Development | Production |
|---------|-------------|------------|
| Cloud Run | $0-5/month | $20-50/month |
| Cloud SQL | $10/month | $25-50/month |
| Storage | $0.02/GB | $1-5/month |
| Networking | $1-5/month | $10-20/month |
| **Total** | **~$15/month** | **~$60-125/month** |

## 🔄 Part 9: CI/CD Pipeline with Cloud Build

### Step 1: Create cloudbuild.yaml

```yaml
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/xgenai:$SHORT_SHA', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/xgenai:$SHORT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'xgenai-app'
      - '--image'
      - 'gcr.io/$PROJECT_ID/xgenai:$SHORT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'

images:
  - 'gcr.io/$PROJECT_ID/xgenai:$SHORT_SHA'
```

### Step 2: Connect GitHub Repository

```bash
# Connect repository
gcloud builds triggers create github \
  --repo-name=AI-website \
  --repo-owner=Sharvanandchaudary \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## 🧪 Part 10: Testing Deployment

### Test Checklist

```bash
# 1. Health check
curl https://YOUR_CLOUD_RUN_URL/health

# 2. Test signup
curl -X POST https://YOUR_CLOUD_RUN_URL/api/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","phone":"1234567890","address":"Test","password":"test123"}'

# 3. Test admin login
curl -X POST https://YOUR_CLOUD_RUN_URL/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@xgenai.com","password":"Admin@123"}'

# 4. Check database
gcloud sql connect xgenai-db --user=xgenai_user --database=xgenai
# Password: YOUR_DB_USER_PASSWORD
# Run: SELECT COUNT(*) FROM users;

# 5. Test email export
curl -X POST https://YOUR_CLOUD_RUN_URL/cron/export-emails \
  -H "X-Appengine-Cron: true"

# 6. Check logs
gcloud run logs read xgenai-app --region=us-central1 --limit=20
```

## 📥 Downloading Email Exports

### Option 1: From Cloud Storage

```bash
# List exports
gsutil ls gs://xgenai-exports/

# Download specific file
gsutil cp gs://xgenai-exports/user_signups_20251129_020000.xlsx ./

# Download all exports
gsutil -m cp -r gs://xgenai-exports/* ./exports/
```

### Option 2: From Cloud Console

1. Go to: https://console.cloud.google.com/storage
2. Click on `xgenai-exports` bucket
3. Download files directly

## 🆘 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check Cloud SQL status
gcloud sql instances describe xgenai-db

# Test connection
gcloud sql connect xgenai-db --user=xgenai_user
```

**2. Cloud Run 503 Errors**
```bash
# Check logs
gcloud run logs read xgenai-app --region=us-central1

# Increase resources
gcloud run services update xgenai-app \
  --memory=2Gi \
  --timeout=600 \
  --region=us-central1
```

**3. Cron Job Not Running**
```bash
# Check scheduler status
gcloud scheduler jobs describe email-export-daily --location=us-central1

# View scheduler logs
gcloud logging read "resource.type=cloud_scheduler_job"
```

## 🔄 Updates & Maintenance

### Deploy New Version

```bash
# Build new image
docker build -t gcr.io/xgenai-app/xgenai:v2.0 .

# Push to registry
docker push gcr.io/xgenai-app/xgenai:v2.0

# Update Cloud Run
gcloud run deploy xgenai-app \
  --image gcr.io/xgenai-app/xgenai:v2.0 \
  --region us-central1
```

### Backup Database

```bash
# Create backup
gcloud sql backups create \
  --instance=xgenai-db \
  --description="Manual backup before update"

# List backups
gcloud sql backups list --instance=xgenai-db

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=xgenai-db \
  --backup-id=BACKUP_ID
```

## 📱 Access Your Application

After successful deployment:

- **Application**: https://YOUR_CLOUD_RUN_URL
- **Admin Dashboard**: https://YOUR_CLOUD_RUN_URL/admin-login.html
- **Signup Page**: https://YOUR_CLOUD_RUN_URL/pages/signup.html
- **Server Status**: https://YOUR_CLOUD_RUN_URL/pages/server-status.html
- **Health Check**: https://YOUR_CLOUD_RUN_URL/health

## 📧 Email Export Schedule

- **Frequency**: Daily at 2:00 AM (configurable in Cloud Scheduler)
- **Output Location**: Cloud Storage bucket `gs://xgenai-exports/`
- **File Format**: Excel (.xlsx)
- **Files Generated**:
  - `user_signups_YYYYMMDD_HHMMSS.xlsx` - All user signups
  - `intern_applications_YYYYMMDD_HHMMSS.xlsx` - All intern applications with job titles

## ✅ Quick Start Summary

```bash
# 1. Setup GCP
gcloud projects create xgenai-app
gcloud config set project xgenai-app

# 2. Create database
gcloud sql instances create xgenai-db --database-version=POSTGRES_15

# 3. Build and push
docker build -t gcr.io/xgenai-app/xgenai:latest .
docker push gcr.io/xgenai-app/xgenai:latest

# 4. Deploy
gcloud run deploy xgenai-app --image gcr.io/xgenai-app/xgenai:latest

# 5. Setup scheduler
gcloud scheduler jobs create http email-export-daily --schedule="0 2 * * *"

# Done! 🎉
```

---

**Support**: For issues, check logs with `gcloud run logs read xgenai-app`  
**Documentation**: https://cloud.google.com/run/docs  
**Last Updated**: November 29, 2025
