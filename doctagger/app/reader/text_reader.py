# Text file reader
import logging
from pathlib import Path

class TextReader:
    """Reader for text files."""
    
    def read_document(self, file_path: Path) -> str:
        """Read a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                logging.debug(f"Successfully read text file: {len(content)} characters")
                return content
        except Exception as e:
            logging.error(f"Error reading text file: {e}")
            raise