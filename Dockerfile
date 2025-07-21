# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=statistical_analysis.settings_docker

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Verify Python version
RUN python --version && python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create static files directory
RUN mkdir -p /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput --settings=statistical_analysis.settings_docker || true

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port (App Runner will set PORT env var)
EXPOSE 8000

# Create startup script for better port handling
RUN echo '#!/bin/bash\n\
echo "Starting application on port 8000"\n\
\n\
# Test database connection\n\
echo "Testing database connection..."\n\
python -c "from django.db import connection; connection.ensure_connection(); print(\"Database connection OK\")" --settings=statistical_analysis.settings_docker || {\n\
    echo "WARNING: Database connection failed"\n\
}\n\
\n\
# Run migrations\n\
echo "Running database migrations..."\n\
python manage.py migrate --noinput --settings=statistical_analysis.settings_docker\n\
\n\
if [ $? -eq 0 ]; then\n\
    echo "Migrations completed successfully"\n\
else\n\
    echo "ERROR: Migration failed"\n\
fi\n\
\n\
echo "Starting web server..."\n\
exec gunicorn --bind 0.0.0.0:8000 statistical_analysis.wsgi:application --workers 2 --timeout 120' > /app/start.sh && \
    chmod +x /app/start.sh

# Health check with proper port handling
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the startup script
CMD ["/app/start.sh"] 
