# debug.py
import os
import sys

# Print current working directory
print(f"Current directory: {os.getcwd()}")

# List directories at the root level
print("\nDirectories at root level:")
for item in os.listdir('.'):
    if os.path.isdir(item):
        print(f"- {item}")

# Check if doctagger directory exists
print("\nChecking for doctagger directory:")
if os.path.exists('doctagger'):
    print("doctagger directory found")
    
    # Check for app.py in doctagger
    if os.path.exists('doctagger/app.py'):
        print("app.py found in doctagger directory")
    else:
        print("app.py NOT found in doctagger directory")
else:
    print("doctagger directory NOT found")

# Print Python path
print("\nPython path:")
for path in sys.path:
    print(path)

print("\nDebug complete!")