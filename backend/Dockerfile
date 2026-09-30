FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for pycurl
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libcurl4-openssl-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Expose Flask port
EXPOSE 5000

# Run Flask application
CMD ["python", "app.py"]
