from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
import os
from pathlib import Path
import tempfile
import shutil
import uuid
import logging
from werkzeug.utils import secure_filename

from ..api.classi_client import ClassiAPI
from ..processor.file_processor import process_file
from ..processor.batch_processor import BatchProcessor

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
        upload_folder.mkdir(exist_ok=True)
        
        # Create a folder for this upload
        upload_dir = upload_folder / unique_id
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / filename
        file.save(file_path)
        
        # Initialize API client
        api = ClassiAPI(current_app.config['API_BASE_URL'])
        
        # Process the file
        result = process_file(
            file_path, 
            api, 
            current_app.config['TAG_NAME'], 
            False,  # Always tag
            False   # Use highest confidence
        )
        
        # Move processed file to processed folder
        processed_folder = Path(current_app.config['PROCESSED_FOLDER'])
        processed_folder.mkdir(exist_ok=True)
        processed_dir = processed_folder / unique_id
        processed_dir.mkdir(exist_ok=True)
        
        # Copy the tagged file to the processed folder
        shutil.copy2(file_path, processed_dir / filename)
        
        return render_template('results.html', 
                              result=result, 
                              filename=filename, 
                              unique_id=unique_id)
    
    return redirect(url_for('web.index'))

@web_bp.route('/batch', methods=['POST'])
def batch_upload():
    if 'files[]' not in request.files:
        flash('No files part')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        flash('No selected files')
        return redirect(request.url)
    
    unique_id = str(uuid.uuid4())
    upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
    upload_folder.mkdir(exist_ok=True)
    
    # Create a folder for this batch
    upload_dir = upload_folder / unique_id
    upload_dir.mkdir(exist_ok=True)
    
    # Save all files
    for file in files:
        filename = secure_filename(file.filename)
        file_path = upload_dir / filename
        file.save(file_path)
    
    # Initialize API client
    api = ClassiAPI(current_app.config['API_BASE_URL'])
    
    # Process the batch
    processor = BatchProcessor(
        api, 
        current_app.config['TAG_NAME'], 
        False,  # Always tag
        current_app.config['MAX_WORKERS'],
        False   # Use highest confidence
    )
    
    results = processor.process_directory(upload_dir)
    
    # Create processed folder
    processed_folder = Path(current_app.config['PROCESSED_FOLDER'])
    processed_folder.mkdir(exist_ok=True)
    processed_dir = processed_folder / unique_id
    processed_dir.mkdir(exist_ok=True)
    
    # Copy all processed files
    for file in upload_dir.glob('*'):
        shutil.copy2(file, processed_dir / file.name)
    
    return render_template('batch_results.html',
                          results=results,
                          unique_id=unique_id)

@web_bp.route('/download/<unique_id>/<filename>')
def download_file(unique_id, filename):
    processed_folder = Path(current_app.config['PROCESSED_FOLDER'])
    return send_from_directory(processed_folder / unique_id, filename)