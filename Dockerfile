FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy application files
COPY web_app.py .

# Create data directory for storing candidates
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "web_app.py"]
