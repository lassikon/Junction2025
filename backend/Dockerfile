FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/startup.sh

# Expose port
EXPOSE 8000

# Run the startup script
CMD ["/app/startup.sh"]
