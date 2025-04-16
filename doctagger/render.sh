#!/bin/bash
# Render start script

# Create necessary directories
mkdir -p /app/uploads /app/processed /app/logs

# Start Gunicorn with the correct WSGI path
gunicorn --bind 0.0.0.0:$PORT wsgi:app