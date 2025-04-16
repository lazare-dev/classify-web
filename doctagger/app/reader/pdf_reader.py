# PDF file reader
import logging
from pathlib import Path
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

class PdfReader:
    """Reader for PDF files."""
    
    def read_document(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        if not HAS_PYPDF2:
            error_msg = "PyPDF2 is required to read PDF files."
            logging.error(error_msg)
            raise ImportError(error_msg)
        
        try:
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                logging.debug(f"PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text() or ""
                        # Clean up any problematic characters
                        page_text = ''.join(ch if ord(ch) < 0x10000 else '?' for ch in page_text)
                        text += page_text + "\n"
                        logging.debug(f"Extracted {len(page_text)} characters from page {page_num}")
                    except Exception as page_error:
                        logging.debug(f"Error extracting text from page {page_num}: {page_error}")
                        text += f"[Error extracting text from page {page_num}]\n"
                    
            logging.debug(f"Total extracted text from PDF: {len(text)} characters")
            return text
        except Exception as e:
            logging.error(f"Error reading PDF: {e}")
            raise