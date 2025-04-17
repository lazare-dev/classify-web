FROM python:3.9-slim
WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application
COPY . .
# Create necessary directories
RUN mkdir -p /app/uploads /app/processed /app/logs
# Debug: List files to verify wsgi.py is present
RUN ls -la /app
RUN echo "---wsgi.py content---"
RUN cat /app/wsgi.py || echo "FILE NOT FOUND"
# Set environment variables
ENV FLASK_APP=wsgi.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Expose port
EXPOSE 8080
# Run the application with the correct WSGI path
CMD ["gunicorn", "--pythonpath", "/app", "--bind", "0.0.0.0:8080", "wsgi:app"]