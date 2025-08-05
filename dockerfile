# Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y build-essential git && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default command: can be overridden
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
