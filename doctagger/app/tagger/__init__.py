# Document Tagger Package
import logging
import sys
import platform
import os
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import taggers
from .pdf_tagger import PdfTagger
from .office_tagger import OfficeTagger
from .text_tagger import TextTagger
from .tagger_factory import TaggerFactory

# Version
__version__ = '1.0.1'

# Check for dependencies
def check_dependencies():
    """Check for required dependencies and log availability."""
    dependencies = {
        'PyPDF2': False,
        'win32com': False
    }
    
    try:
        import PyPDF2
        dependencies['PyPDF2'] = True
    except ImportError:
        logging.warning("PyPDF2 not found. PDF tagging functionality will be limited.")
    
    if platform.system() == 'Windows':
        try:
            import win32com.client
            dependencies['win32com'] = True
        except ImportError:
            logging.warning("win32com not found. Office COM automation will be unavailable.")
    else:
        logging.info("Not running on Windows. Office COM automation and ADS will be unavailable.")
    
    # Log dependency status
    logging.debug("Dependency check results:")
    for dep, available in dependencies.items():
        logging.debug(f"  {dep}: {'Available' if available else 'Not available'}")
    
    return dependencies

# Run dependency check on import
dependencies = check_dependencies()

# Define convenience method for tagging files
def tag_file(file_path, tag_name, tag_value):
    """
    Tag a file with metadata.
    
    Args:
        file_path (str or Path): Path to the file to tag
        tag_name (str): Name of the tag/metadata field
        tag_value (str): Value to set for the tag
        
    Returns:
        bool: True if tagging succeeded, False otherwise
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    try:
        tagger = TaggerFactory.get_tagger(file_path)
        return tagger.tag_document(file_path, tag_name, tag_value)
    except Exception as e:
        logging.error(f"Error tagging file {file_path}: {e}")
        return False

# Define what's exposed at package level
__all__ = [
    'PdfTagger', 
    'OfficeTagger', 
    'TextTagger',
    'TaggerFactory',
    'tag_file'
]