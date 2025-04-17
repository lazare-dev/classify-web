#!/bin/bash
echo "Current directory: $(pwd)"
echo "Listing files in current directory:"
ls -la
echo "Checking for wsgi.py:"
if [ -f wsgi.py ]; then
  echo "wsgi.py found in current directory"
else
  echo "wsgi.py NOT found in current directory"
fi

export PYTHONPATH=$(pwd)
echo "PYTHONPATH set to: $PYTHONPATH"

exec gunicorn --pythonpath $(pwd) wsgi:app --bind 0.0.0.0:8080