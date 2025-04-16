# Reader factory module
import logging
import mimetypes
from pathlib import Path
from .text_reader import TextReader
from .pdf_reader import PdfReader
from .office_reader import OfficeReader

class ReaderFactory:
    """Factory for creating document readers."""
    
    @staticmethod
    def get_reader(file_path: Path):
        """Get the appropriate reader for the file type."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        mime_type, _ = mimetypes.guess_type(str(file_path))
        logging.debug(f"File MIME type: {mime_type}")
        
        if mime_type == 'application/pdf' or file_path.suffix.lower() == '.pdf':
            return PdfReader()
        elif mime_type in [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        ] or file_path.suffix.lower() in ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt']:
            return OfficeReader()
        else:
            # Default to text reader for all other types
            return TextReader()