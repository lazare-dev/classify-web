# Text file tagger module
import logging
import os
import sys
import tempfile
import shutil
import re
from pathlib import Path

class TextTagger:
    """Tagger for text files."""
    
    def tag_document(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Add or update metadata in a text file.
        Returns True if successful, False otherwise.
        """
        if not file_path.exists():
            logging.error(f"Error: File not found: {file_path}")
            return False
        
        logging.info(f"Tagging text document: {file_path}")
        logging.info(f"Tag: {tag_name}={tag_value}")
        
        # Try multiple methods to ensure at least one works
        # Order of methods:
        # 1. Windows ADS (if available)
        # 2. Metadata file
        # 3. Comment header (for code files)
        # 4. Binary marker as last resort
        
        # Try Windows ADS first (if on Windows)
        if sys.platform == 'win32':
            if self._tag_with_ads(file_path, tag_name, tag_value):
                return True
        
        # Try metadata file next (works on all platforms)
        if self._tag_with_metadata_file(file_path, tag_name, tag_value):
            return True
            
        # Try comment header for known code/markup files
        file_ext = file_path.suffix.lower()
        code_extensions = [
            '.py', '.js', '.java', '.c', '.cpp', '.h', '.cs', '.sh', 
            '.php', '.rb', '.pl', '.lua', '.sql', '.html', '.htm', 
            '.xml', '.css', '.md', '.json', '.yaml', '.yml', '.bash',
            '.ps1', '.bat', '.cmd', '.r', '.groovy', '.kt', '.ts'
        ]
        
        if file_ext in code_extensions and self._tag_with_comments(file_path, tag_name, tag_value):
            return True
        
        # Last resort: Binary marker
        return self._tag_with_binary_marker(file_path, tag_name, tag_value)
    
    def _tag_with_ads(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Add metadata using NTFS Alternate Data Streams on Windows.
        Won't work on non-NTFS filesystems.
        """
        if sys.platform != 'win32':
            logging.debug("ADS tagging only available on Windows")
            return False
            
        try:
            # Create ADS filename for metadata
            ads_path = f"{file_path}:metadata"
            
            # Write metadata to ADS
            with open(ads_path, 'w', encoding='utf-8') as f:
                f.write(f"{tag_name}: {tag_value}")
                
            logging.debug(f"Successfully created ADS: {ads_path}")
            return True
            
        except Exception as e:
            logging.debug(f"Error creating ADS: {e}")
            return False
    
    def _tag_with_metadata_file(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Create a separate .metadata file alongside the original.
        Works on all platforms and filesystems.
        """
        try:
            # Create metadata filename
            meta_path = file_path.with_suffix(file_path.suffix + ".metadata")
            
            # Check if metadata file already exists
            if meta_path.exists():
                # Read existing metadata
                with open(meta_path, 'r', encoding='utf-8', errors='replace') as f:
                    meta_content = f.read()
                
                # Parse metadata
                meta_dict = {}
                for line in meta_content.splitlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        meta_dict[key.strip()] = value.strip()
                
                # Update with new tag
                meta_dict[tag_name] = tag_value
                
                # Write updated metadata
                with open(meta_path, 'w', encoding='utf-8') as f:
                    for key, value in meta_dict.items():
                        f.write(f"{key}: {value}\n")
                
                logging.debug(f"Updated existing metadata file: {meta_path}")
            else:
                # Create new metadata file
                with open(meta_path, 'w', encoding='utf-8') as f:
                    f.write(f"{tag_name}: {tag_value}\n")
                logging.debug(f"Created new metadata file: {meta_path}")
            
            return True
            
        except Exception as e:
            logging.debug(f"Error creating metadata file: {e}")
            return False
    
    def _tag_with_comments(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Add metadata as comments in the file.
        Works well for code files, scripts, etc.
        """
        try:
            # Read the entire file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Determine comment syntax based on file extension
            file_ext = file_path.suffix.lower()
            
            # Comment styles for different file types
            comment_styles = {
                # Single line comments
                '.py': ('#', ''),
                '.rb': ('#', ''),
                '.pl': ('#', ''),
                '.sh': ('#', ''),
                '.bash': ('#', ''),
                '.ps1': ('#', ''),
                '.r': ('#', ''),
                '.yaml': ('#', ''),
                '.yml': ('#', ''),
                
                # C-style comments
                '.js': ('//', ''),
                '.ts': ('//', ''),
                '.java': ('//', ''),
                '.c': ('//', ''),
                '.cpp': ('//', ''),
                '.h': ('//', ''),
                '.cs': ('//', ''),
                '.php': ('//', ''),
                '.swift': ('//', ''),
                '.kt': ('//', ''),
                '.groovy': ('//', ''),
                
                # SQL-style
                '.sql': ('--', ''),
                '.lua': ('--', ''),
                
                # HTML/XML
                '.html': ('<!--', '-->'),
                '.htm': ('<!--', '-->'),
                '.xml': ('<!--', '-->'),
                
                # CSS
                '.css': ('/*', '*/'),
                
                # Batch files
                '.bat': ('REM', ''),
                '.cmd': ('REM', '')
            }
            
            # Default to # for unknown types
            comment_start, comment_end = comment_styles.get(file_ext, ('#', ''))
            
            # Create metadata comment line
            metadata_line = f"{comment_start} METADATA: {tag_name}={tag_value} {comment_end}\n"
            
            # Check if there's already metadata
            metadata_pattern = re.compile(
                f"{re.escape(comment_start)}\\s*METADATA:\\s*{re.escape(tag_name)}\\s*=.*?{re.escape(comment_end) if comment_end else '$'}", 
                re.MULTILINE
            )
            
            if metadata_pattern.search(content):
                # Replace existing metadata
                new_content = metadata_pattern.sub(metadata_line.strip(), content)
            else:
                # Add metadata at the top, after any shebang line
                lines = content.splitlines()
                
                # Check for shebang or encoding comment at the top
                if lines and (lines[0].startswith('#!') or 
                             (file_ext == '.py' and 
                              (lines[0].startswith('# -*- coding') or 
                               lines[0].startswith('# coding')))):
                    # Insert after the first line
                    new_content = lines[0] + '\n' + metadata_line + '\n'.join(lines[1:])
                else:
                    # Insert at the top
                    new_content = metadata_line + content
            
            # Write the file back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logging.debug(f"Added metadata comment to {file_path}")
            return True
            
        except Exception as e:
            logging.debug(f"Error adding comment tag: {e}")
            return False
    
    def _tag_with_binary_marker(self, file_path: Path, tag_name: str, tag_value: str) -> bool:
        """
        Add a binary marker to the end of the file.
        Last resort method that should work for any file.
        """
        try:
            # Create marker string
            marker = f"\n### METADATA: {tag_name}={tag_value} ###\n"
            marker_bytes = marker.encode('utf-8')
            
            # Read original file in binary mode
            with open(file_path, 'rb') as f:
                original_data = f.read()
                
            # Check if the marker already exists
            if marker.encode('utf-8') in original_data:
                logging.debug(f"Binary marker already exists in {file_path}")
                return True
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Write original content
                temp_file.write(original_data)
                
                # Add newline if needed
                if original_data and not original_data.endswith(b'\n'):
                    temp_file.write(b'\n')
                    
                # Write marker
                temp_file.write(marker_bytes)
            
            # Replace original with the new file
            shutil.move(temp_file.name, file_path)
            
            logging.debug(f"Added binary marker to {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding binary marker: {e}")
            return False