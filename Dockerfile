# Satyameva - Blockchain Academic Credential Verification
# Production Dockerfile optimized for Render & Cloud Platforms

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    SATYAMEVA_ENV=production

WORKDIR /app

# Install system dependencies for cryptography / image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure instance directory exists for SQLite / storage
RUN mkdir -p /app/instance

# Expose default port
EXPOSE 5000

# Start with dynamic port binding for Render ($PORT) with fallback to 5000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 --timeout 120 run:app"]
