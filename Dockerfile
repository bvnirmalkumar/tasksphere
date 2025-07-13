FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies for performance and security
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for robust logging and import paths
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Use a non-root user for security (optional, requires user setup in Dockerfile and app folder permissions)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "taskqueue.api.monitor:app", "--host", "0.0.0.0", "--port", "8000", "--workers=4"]