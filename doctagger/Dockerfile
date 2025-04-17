FROM python:3.9-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/processed /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run a simple app that doesn't depend on complex imports
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]