# Satyameva Blockchain Credential Verification System
# Production Dockerfile
FROM python:3.11-slim

# System setup & security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    SATYAMEVA_ENV=production

WORKDIR /app

# Install system dependencies (build-essential, libpq for postgres, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt gunicorn psycopg2-binary

# Copy application source
COPY . .

# Ensure instance and storage directories exist with appropriate permissions
RUN mkdir -p /app/instance && chmod -R 775 /app/instance

# Create non-privileged user for security
RUN useradd -m -u 1000 satyameva && chown -R satyameva:satyameva /app
USER satyameva

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:5000/verify || exit 1

# Production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "2", "--timeout", "60", "run:app"]
