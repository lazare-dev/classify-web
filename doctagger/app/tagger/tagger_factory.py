# Tagger factory module
import logging
import mimetypes
from pathlib import Path
from .pdf_tagger import PdfTagger
from .office_tagger import OfficeTagger
import sys

class TaggerFactory:
    """Factory for creating document taggers."""
    
    @staticmethod
    def get_tagger(file_path: Path):
        """Get the appropriate tagger for the file type."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        mime_type, _ = mimetypes.guess_type(str(file_path))
        logging.debug(f"File MIME type for tagging: {mime_type}")
        
        if mime_type == 'application/pdf' or file_path.suffix.lower() == '.pdf':
            return PdfTagger()
        elif mime_type in [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/msword',
            'application/vnd.ms-excel',
            'application/vnd.ms-powerpoint'
        ] or file_path.suffix.lower() in ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']:
            return OfficeTagger()
        else:
            # Default to Office tagger which has fallbacks for other file types
            return OfficeTagger()