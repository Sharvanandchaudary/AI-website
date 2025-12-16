# ZGENAI - Go Application for GCP

A high-performance Go backend for ZGENAI deployed on Google Cloud Platform.

## Project Structure

```
zgenai-go/
├── cmd/
│   └── server/          # Application entry point
├── internal/
│   ├── config/          # Configuration management
│   ├── handlers/        # HTTP handlers
│   ├── middleware/      # HTTP middleware
│   ├── models/          # Data models
│   ├── repository/      # Database layer
│   └── services/        # Business logic
├── pkg/
│   ├── database/        # Database utilities
│   └── utils/           # Helper functions
├── static/              # Static files (HTML, CSS, JS)
├── deployments/         # Deployment configurations
│   ├── cloudbuild.yaml  # Cloud Build config
│   └── app.yaml         # App Engine config
├── go.mod               # Go modules
├── go.sum               # Dependencies lock
└── .env.example         # Environment variables template
```

## Features

- ✅ RESTful API with Go standard library + Gorilla Mux
- ✅ PostgreSQL integration with pgx
- ✅ JWT authentication
- ✅ CORS support
- ✅ File upload handling
- ✅ Email notifications
- ✅ Excel export functionality
- ✅ GCP Cloud SQL integration
- ✅ GCP Cloud Storage for file uploads
- ✅ Structured logging
- ✅ Graceful shutdown

## Prerequisites

- Go 1.21 or higher
- PostgreSQL 15+
- GCP Account with billing enabled
- gcloud CLI installed

## Local Development

```bash
# Install dependencies
go mod download

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
# Set DATABASE_URL, JWT_SECRET, etc.

# Run the application
go run cmd/server/main.go
```

## GCP Deployment

### Option 1: Cloud Run (Recommended)

```bash
# Build and deploy
gcloud run deploy zgenai \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=your_connection_string
```

### Option 2: App Engine

```bash
# Deploy to App Engine
gcloud app deploy deployments/app.yaml
```

### Option 3: GKE (Kubernetes)

```bash
# Build Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/zgenai:latest .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/zgenai:latest

# Deploy to GKE
kubectl apply -f deployments/k8s/
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET` | Secret key for JWT tokens | Yes |
| `PORT` | Server port (default: 8080) | No |
| `GCP_PROJECT_ID` | GCP Project ID | Yes |
| `GCP_BUCKET_NAME` | Cloud Storage bucket name | Yes |
| `ADMIN_EMAIL` | Admin email | Yes |
| `ADMIN_PASSWORD` | Admin password | Yes |
| `SENDGRID_API_KEY` | SendGrid API key for emails | No |

## API Endpoints

### Public
- `GET /` - Homepage
- `POST /api/applications` - Submit job application
- `POST /api/signup` - User signup
- `POST /api/login` - User login

### Admin (Protected)
- `POST /api/admin/login` - Admin login
- `GET /api/admin/applications` - List all applications
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/export/users` - Export users to Excel
- `GET /api/admin/export/applications` - Export applications to Excel

## Database Setup

The application automatically creates tables on first run. Schema includes:
- users
- applications
- sessions
- emails
- selected_interns

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection prevention with parameterized queries
- CORS configuration
- Rate limiting
- Input validation

## Monitoring & Logging

- Structured logging with zerolog
- GCP Cloud Logging integration
- Error tracking
- Performance metrics

## License

MIT License - See LICENSE file for details
