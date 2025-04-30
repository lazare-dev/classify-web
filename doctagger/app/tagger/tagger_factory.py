# Tagger factory module
import logging
import mimetypes
from pathlib import Path
from .pdf_tagger import PdfTagger
from .office_tagger import OfficeTagger
from .text_tagger import TextTagger
import sys

class TaggerFactory:
    """Factory for creating document taggers."""
    
    @staticmethod
    def get_tagger(file_path: Path):
        """Get the appropriate tagger for the file type."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension and mime type
        ext = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        logging.debug(f"File MIME type for tagging: {mime_type}")
        
        # Define text file extensions
        text_extensions = [
            '.txt', '.log', '.md', '.markdown', '.csv', '.tsv',
            '.py', '.js', '.ts', '.html', '.htm', '.css', '.xml', '.json', 
            '.yaml', '.yml', '.ini', '.cfg', '.conf', '.sh', '.bash',
            '.bat', '.ps1', '.cmd', '.java', '.c', '.cpp', '.h', '.cs', 
            '.go', '.rs', '.rb', '.pl', '.php', '.sql', '.lua', '.r',
            '.swift', '.kt', '.groovy', '.scala', '.tex'
        ]
        
        # Define text MIME types
        text_mime_types = [
            'text/plain', 'text/csv', 'text/markdown', 'text/html', 
            'text/css', 'text/xml', 'application/json', 'application/x-yaml',
            'application/javascript', 'application/typescript',
            'text/x-python', 'text/x-java', 'text/x-c', 'text/x-script',
            'text/x-shellscript', 'application/x-sh', 'application/x-bat'
        ]
        
        # Check for text files first (highest priority)
        if ext in text_extensions or (mime_type and 
                                      (mime_type.startswith('text/') or 
                                       mime_type in text_mime_types)):
            logging.debug(f"Using TextTagger for file: {file_path}")
            return TextTagger()
        
        # Then check for PDF files
        elif ext == '.pdf' or mime_type == 'application/pdf':
            logging.debug(f"Using PdfTagger for file: {file_path}")
            return PdfTagger()
        
        # Then check for Office documents
        elif ext in ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt'] or mime_type in [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/msword',
            'application/vnd.ms-excel',
            'application/vnd.ms-powerpoint'
        ]:
            logging.debug(f"Using OfficeTagger for file: {file_path}")
            return OfficeTagger()
        
        # For unknown/binary file types
        else:
            # Try to determine if it might be a text file by reading the first few bytes
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(512)
                    # Check if content looks like text (high proportion of ASCII chars)
                    ascii_chars = sum(1 for b in header if 32 <= b <= 126 or b in (9, 10, 13))
                    if ascii_chars / len(header) > 0.8:  # >80% printable ASCII
                        logging.debug(f"File appears to be text based on content analysis: {file_path}")
                        return TextTagger()
            except Exception as e:
                logging.debug(f"Error analyzing file content: {e}")
            
            # Default to OfficeTagger which has fallbacks for other file types
            logging.debug(f"Using OfficeTagger (with fallbacks) for unknown file type: {file_path}")
            return OfficeTagger()