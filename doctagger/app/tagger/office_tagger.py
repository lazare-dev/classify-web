# Office document tagger
import logging
import os
import sys
import tempfile
import shutil
import zipfile
import traceback
from pathlib import Path

# For Windows file properties
try:
    import win32com.client
    import pythoncom
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

class OfficeTagger:
    """Tagger for Office documents and other files."""
    
    def tag_document(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Add or update metadata on a document.
        Returns True if successful, False otherwise.
        """
        file_ext = file_path.suffix.lower()
        
        # Check if file exists
        if not file_path.exists():
            logging.error(f"Error: File not found: {file_path}")
            return False
        
        logging.info(f"Tagging document: {file_path}")
        logging.info(f"Tag: {tag_name}={tag_value}")
        
        # First, remove any existing meta files that might have been created previously
        try:
            meta_path = file_path.with_suffix(file_path.suffix + ".meta")
            if meta_path.exists():
                os.remove(meta_path)
                logging.debug(f"Removed existing meta file: {meta_path}")
        except Exception as e:
            logging.debug(f"Error removing meta file: {e}")
        
        # Tag based on file type
        if file_ext in ['.docx', '.xlsx', '.pptx']:
            # Modern Office files
            return self._tag_office_document(file_path, tag_name, tag_value)
        elif file_ext in ['.doc', '.xls', '.ppt'] and HAS_WIN32COM:
            # Legacy Office files with COM
            return self._tag_with_office_app(file_path, tag_name, tag_value)
        else:
            # Other files - try multiple methods
            return self._tag_with_multiple_methods(file_path, tag_name, tag_value)
    
    def _tag_office_document(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Tag Office Open XML documents by modifying core.xml and app.xml.
        """
        try:
            # Create temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                logging.debug(f"Created temporary directory: {temp_dir_path}")
                
                # Copy original file to temp location
                temp_file = temp_dir_path / "original.zip"
                shutil.copy2(file_path, temp_file)
                logging.debug(f"Copied original file to: {temp_file}")
                
                # Extract the zip
                extract_dir = temp_dir_path / "extracted"
                extract_dir.mkdir()
                
                # Extract ZIP file
                with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Update core.xml if it exists
                core_xml_path = extract_dir / "docProps" / "core.xml"
                updated_core = False
                
                if core_xml_path.exists():
                    logging.debug(f"Reading core.xml: {core_xml_path}")
                    with open(core_xml_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update keywords
                    if "<cp:keywords>" in content:
                        if "</cp:keywords>" in content:
                            content = content.replace("</cp:keywords>", f"{tag_name}: {tag_value}</cp:keywords>")
                            updated_core = True
                    else:
                        content = content.replace("</cp:coreProperties>", 
                                                f"<cp:keywords>{tag_name}: {tag_value}</cp:keywords></cp:coreProperties>")
                        updated_core = True
                    
                    # Update subject
                    if "<dc:subject>" in content:
                        if "</dc:subject>" in content:
                            content = content.replace("</dc:subject>", f"{tag_name}: {tag_value}</dc:subject>")
                            updated_core = True
                    else:
                        content = content.replace("</cp:coreProperties>", 
                                                f"<dc:subject>{tag_name}: {tag_value}</dc:subject></cp:coreProperties>")
                        updated_core = True
                    
                    # Write updated content
                    if updated_core:
                        logging.debug("Writing updated core.xml")
                        with open(core_xml_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                
                # Update app.xml if it exists
                app_xml_path = extract_dir / "docProps" / "app.xml"
                if app_xml_path.exists():
                    logging.debug(f"Reading app.xml: {app_xml_path}")
                    try:
                        with open(app_xml_path, 'r', encoding='utf-8') as f:
                            app_content = f.read()
                        
                        # Add company tag
                        if "<Company>" in app_content:
                            if "</Company>" in app_content:
                                app_content = app_content.replace("</Company>", f"{tag_name}: {tag_value}</Company>")
                                updated_core = True
                        else:
                            app_content = app_content.replace("</Properties>", 
                                                        f"<Company>{tag_name}: {tag_value}</Company></Properties>")
                            updated_core = True
                        
                        # Write updated app.xml
                        logging.debug("Writing updated app.xml")
                        with open(app_xml_path, 'w', encoding='utf-8') as f:
                            f.write(app_content)
                    except Exception as app_error:
                        logging.debug(f"Error updating app.xml: {app_error}")
                
                # If we couldn't update the files, try a different approach
                if not updated_core:
                    logging.warning(f"Could not update core.xml or app.xml in {file_path}")
                    return self._tag_with_multiple_methods(file_path, tag_name, tag_value)
                
                # Create new zip file
                new_zip = temp_dir_path / "new.zip"
                logging.debug(f"Creating new zip file: {new_zip}")
                
                # Create zip with all files
                with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(extract_dir):
                        for file in files:
                            file_path_in_zip = os.path.relpath(os.path.join(root, file), extract_dir)
                            zipf.write(os.path.join(root, file), file_path_in_zip)
                
                # Replace original file
                logging.debug(f"Replacing original file with tagged version")
                try:
                    os.remove(str(file_path))
                except PermissionError:
                    logging.debug("Could not remove original file directly, trying shutil.move with replacement")
                
                shutil.copy2(new_zip, file_path)
                
                logging.info(f"Successfully tagged Office document {file_path} with {tag_name}: {tag_value}")
                return True
                
        except Exception as e:
            logging.error(f"Error tagging Office document: {e}")
            logging.debug(f"Falling back to alternative tagging methods")
            return self._tag_with_multiple_methods(file_path, tag_name, tag_value)
    
    def _tag_with_office_app(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """Tag Office document using Office application automation."""
        if not HAS_WIN32COM:
            return False
            
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Get file extension to determine which Office app to use
            file_ext = file_path.suffix.lower()
            abs_path = str(file_path.resolve())
            
            # Different handling based on file type
            if file_ext in ['.doc', '.docx']:
                # Try Word
                try:
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False
                    doc = word.Documents.Open(abs_path)
                    
                    # Try setting various properties
                    try:
                        doc.Keywords = f"{tag_name}: {tag_value}"
                    except:
                        pass
                        
                    try:
                        doc.Comments = f"{tag_name}: {tag_value}"
                    except:
                        pass
                        
                    try:
                        doc.Subject = f"{tag_name}: {tag_value}"
                    except:
                        pass
                    
                    # Save and close
                    doc.Save()
                    doc.Close()
                    word.Quit()
                    
                    logging.info(f"Tagged Word document {file_path} with Office automation")
                    return True
                except Exception as word_err:
                    logging.debug(f"Word automation error: {word_err}")
                    
            elif file_ext in ['.xls', '.xlsx']:
                # Try Excel
                try:
                    excel = win32com.client.Dispatch("Excel.Application")
                    excel.Visible = False
                    excel.DisplayAlerts = False
                    workbook = excel.Workbooks.Open(abs_path)
                    
                    # Try setting various properties
                    try:
                        workbook.Keywords = f"{tag_name}: {tag_value}"
                    except:
                        pass
                        
                    try:
                        workbook.Comments = f"{tag_name}: {tag_value}"
                    except:
                        pass
                        
                    try:
                        workbook.Subject = f"{tag_name}: {tag_value}"
                    except:
                        pass
                    
                    # Save and close
                    workbook.Save()
                    workbook.Close()
                    excel.Quit()
                    
                    logging.info(f"Tagged Excel document {file_path} with Office automation")
                    return True
                except Exception as excel_err:
                    logging.debug(f"Excel automation error: {excel_err}")
                    
            elif file_ext in ['.ppt', '.pptx']:
                # Try PowerPoint
                try:
                    ppt = win32com.client.Dispatch("PowerPoint.Application")
                    ppt.Visible = False
                    presentation = ppt.Presentations.Open(abs_path)
                    
                    # Try setting various properties
                    try:
                        presentation.Keywords = f"{tag_name}: {tag_value}"
                    except:
                        pass
                        
                    try:
                        presentation.Comments = f"{tag_name}: {tag_value}"
                    except:
                        pass
                        
                    try:
                        presentation.Subject = f"{tag_name}: {tag_value}"
                    except:
                        pass
                    
                    # Save and close
                    presentation.Save()
                    presentation.Close()
                    ppt.Quit()
                    
                    logging.info(f"Tagged PowerPoint document {file_path} with Office automation")
                    return True
                except Exception as ppt_err:
                    logging.debug(f"PowerPoint automation error: {ppt_err}")
            
            return False
            
        except Exception as e:
            logging.error(f"Error in Office application automation: {e}")
            return False
        finally:
            pythoncom.CoUninitialize()
    
    def _tag_with_multiple_methods(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """Try multiple methods to tag files."""
        # Try Windows ADS if available
        if sys.platform == 'win32':
            try:
                # Create ADS filename
                ads_path = f"{file_path}:metadata"
                
                # Write metadata to ADS
                with open(ads_path, 'w', encoding='utf-8') as f:
                    f.write(f"{tag_name}: {tag_value}")
                    
                logging.debug(f"Successfully created ADS: {ads_path}")
                return True
            except Exception as e:
                logging.debug(f"Error creating ADS: {e}")
        
        # Try binary marker as last resort
        try:
            # Create marker string
            marker_text = f"### METADATA: {tag_name}={tag_value} ###"
            marker_bytes = marker_text.encode('utf-8')
            
            # Read original file
            with open(file_path, 'rb') as f:
                original_data = f.read()
                
            # Write original data with marker appended
            with open(file_path, 'wb') as f:
                f.write(original_data)
                # Add a newline if the file doesn't end with one
                if original_data and original_data[-1:] not in [b'\n', b'\r']:
                    f.write(b'\n')
                f.write(marker_bytes)
                
            logging.debug(f"Added binary marker to {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error adding binary marker: {e}")
            return False