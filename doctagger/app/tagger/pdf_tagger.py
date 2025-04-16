# PDF tagger module
import logging
import os
import shutil
from pathlib import Path

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

class PdfTagger:
    """Tagger for PDF documents."""
    
    def tag_document(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """Tag PDF document with metadata."""
        if not HAS_PYPDF2:
            logging.error("Cannot tag PDF: PyPDF2 is not installed.")
            logging.debug(f"Would have tagged with: {tag_name}={tag_value}")
            return False
        
        try:
            # Read the existing PDF
            reader = PyPDF2.PdfReader(str(file_path))
            writer = PyPDF2.PdfWriter()
            
            # Copy all pages from reader to writer
            logging.debug(f"Copying {len(reader.pages)} pages to new PDF")
            for page in reader.pages:
                writer.add_page(page)
                
            # Update metadata
            metadata = reader.metadata.copy() if reader.metadata else {}
            
            # Log existing metadata
            logging.debug("Existing PDF metadata:")
            for key, value in metadata.items() if metadata else {}:
                logging.debug(f"  {key}: {value}")
            
            # Add the tag as different formats to ensure DLP detection
            metadata[f"/{tag_name}"] = tag_value
            metadata[f"/Keywords"] = f"{tag_name}: {tag_value}"
            metadata[f"/Subject"] = f"{tag_name}: {tag_value}"
            
            writer.add_metadata(metadata)
            
            # Save the file with new metadata
            temp_path = str(file_path) + ".tmp"
            with open(temp_path, 'wb') as f:
                writer.write(f)
            
            # Replace the original file
            logging.debug(f"Replacing original PDF with tagged version")
            os.remove(str(file_path))  # Explicitly remove to handle Windows file locking
            shutil.move(temp_path, str(file_path))
            
            logging.info(f"Successfully tagged PDF {file_path} with {tag_name}: {tag_value}")
            return True
            
        except Exception as e:
            logging.error(f"Error tagging PDF: {e}")
            return False