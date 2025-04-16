#!/usr/bin/env python3
import os
import sys
import subprocess

def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def create_empty_file(path):
    """Create an empty file if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
        print(f"Created file: {path}")
    else:
        print(f"File already exists: {path}")

def install_requirements():
    """Install the required packages."""
    requirements = [
        "flask",
        "gunicorn",
        "requests",
        "PyPDF2",
        "python-docx",
        "openpyxl",
        "python-pptx"
    ]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
        print("Successfully installed requirements.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False
    
    # Create requirements.txt file
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    print("Created requirements.txt file.")
    return True

def main():
    # Base directory
    base_dir = os.path.abspath("doctagger")
    create_directory(base_dir)
    
    # App structure
    app_dir = os.path.join(base_dir, "app")
    create_directory(app_dir)
    create_empty_file(os.path.join(app_dir, "__init__.py"))
    create_empty_file(os.path.join(app_dir, "config.py"))
    
    # Reader module
    reader_dir = os.path.join(app_dir, "reader")
    create_directory(reader_dir)
    create_empty_file(os.path.join(reader_dir, "__init__.py"))
    create_empty_file(os.path.join(reader_dir, "text_reader.py"))
    create_empty_file(os.path.join(reader_dir, "pdf_reader.py"))
    create_empty_file(os.path.join(reader_dir, "office_reader.py"))
    create_empty_file(os.path.join(reader_dir, "reader_factory.py"))
    
    # Tagger module
    tagger_dir = os.path.join(app_dir, "tagger")
    create_directory(tagger_dir)
    create_empty_file(os.path.join(tagger_dir, "__init__.py"))
    create_empty_file(os.path.join(tagger_dir, "pdf_tagger.py"))
    create_empty_file(os.path.join(tagger_dir, "office_tagger.py"))
    create_empty_file(os.path.join(tagger_dir, "tagger_factory.py"))
    
    # API module
    api_dir = os.path.join(app_dir, "api")
    create_directory(api_dir)
    create_empty_file(os.path.join(api_dir, "__init__.py"))
    create_empty_file(os.path.join(api_dir, "classi_client.py"))
    
    # Processor module
    processor_dir = os.path.join(app_dir, "processor")
    create_directory(processor_dir)
    create_empty_file(os.path.join(processor_dir, "__init__.py"))
    create_empty_file(os.path.join(processor_dir, "file_processor.py"))
    create_empty_file(os.path.join(processor_dir, "batch_processor.py"))
    
    # Web interface module
    web_dir = os.path.join(app_dir, "web")
    create_directory(web_dir)
    create_empty_file(os.path.join(web_dir, "__init__.py"))
    create_empty_file(os.path.join(web_dir, "routes.py"))
    
    # Templates directory
    templates_dir = os.path.join(web_dir, "templates")
    create_directory(templates_dir)
    create_empty_file(os.path.join(templates_dir, "index.html"))
    create_empty_file(os.path.join(templates_dir, "results.html"))
    
    # Other directories
    static_dir = os.path.join(base_dir, "static")
    create_directory(static_dir)
    
    uploads_dir = os.path.join(base_dir, "uploads")
    create_directory(uploads_dir)
    
    processed_dir = os.path.join(base_dir, "processed")
    create_directory(processed_dir)
    
    # Main application files
    create_empty_file(os.path.join(base_dir, "Dockerfile"))
    create_empty_file(os.path.join(base_dir, "docker-compose.yml"))
    create_empty_file(os.path.join(base_dir, "wsgi.py"))
    
    # Install required packages
    print("\nInstalling requirements...")
    install_requirements()
    
    print("\nSetup complete!")

if __name__ == "__main__":
    main()