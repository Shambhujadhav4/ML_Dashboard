FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (needed for compiling some C-extensions if necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure models and uploads directories exist
RUN mkdir -p /app/models /app/uploads

# Run Gunicorn with Uvicorn workers
CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
