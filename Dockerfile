# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for email export
RUN pip install --no-cache-dir openpyxl schedule

# Copy application files
COPY . .

# Create directory for exports
RUN mkdir -p /app/exports

# Copy and set up cron job
COPY crontab /etc/cron.d/email-export-cron
RUN chmod 0644 /etc/cron.d/email-export-cron
RUN crontab /etc/cron.d/email-export-cron

# Create log file for cron
RUN touch /var/log/cron.log

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start cron and Flask app
CMD cron && gunicorn --bind 0.0.0.0:8080 --workers 4 --threads 2 --timeout 120 backend:app
