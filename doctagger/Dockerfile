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
ENV FLASK_APP=wsgi.py
ENV PYTHONUNBUFFERED=1
# Make start script executable
COPY start.sh .
RUN chmod +x start.sh
# Expose port
EXPOSE 8080
# Run the application using the start script
CMD ["./start.sh"]