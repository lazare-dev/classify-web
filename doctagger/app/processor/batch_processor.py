# Batch processor module
import logging
import datetime
import json
import traceback
import queue
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

from ..api.classi_client import ClassiAPI
from .file_processor import process_file

class BatchProcessor:
    """Process a directory of files with threading."""
    
    def __init__(self, api: ClassiAPI, tag_name: str, no_tag: bool, max_workers: int = 5, use_first_match: bool = False):
        self.api = api
        self.tag_name = tag_name
        self.no_tag = no_tag
        self.max_workers = max_workers
        self.use_first_match = use_first_match
        self.results_queue = queue.Queue()
        self.processing_error = None
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "classification_results": {},
            "errors": [],
            "start_time": datetime.datetime.now().isoformat(),
        }
    
    def process_file_worker(self, file_path: Path):
        """Worker function to process a file and put results in queue."""
        try:
            result = process_file(file_path, self.api, self.tag_name, self.no_tag, self.use_first_match)
            self.results_queue.put(result)
        except Exception as e:
            error_data = {
                "error": str(e),
                "file": str(file_path)
            }
            self.results_queue.put(error_data)
            logging.error(f"Worker error processing {file_path}: {e}")
    
    def process_directory(self, directory_path: Path) -> Dict[str, Any]:
        """Process all documents in a directory with threading.
        
        Returns a dictionary with statistics about the processing.
        """
        logging.info(f"Processing directory: {directory_path}")
        if self.use_first_match:
            logging.info("Using first match found for classification (--first option)")
            logging.info("Processing will stop at first match for each file")
            
        # Check if directory exists
        if not directory_path.exists() or not directory_path.is_dir():
            logging.error(f"Directory not found: {directory_path}")
            return {"error": f"Directory not found: {directory_path}"}
        
        # Get all files in the directory
        all_files = [f for f in directory_path.glob("*") if f.is_file()]
        self.stats["total_files"] = len(all_files)
        
        logging.info(f"Found {len(all_files)} files to process")
        
        # Create a progress tracker
        processed_count = 0
        
        # Process files with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files for processing
            futures = {executor.submit(self.process_file_worker, file_path): file_path for file_path in all_files}
            
            # Track progress while waiting for results
            while processed_count < len(all_files):
                try:
                    # Try to get a result from the queue with timeout
                    result = self.results_queue.get(timeout=0.5)
                    
                    # Process the result
                    if "error" in result:
                        self.stats["errors"].append({
                            "file": result.get("file", "Unknown"),
                            "error": result["error"]
                        })
                        logging.error(f"Error processing {result.get('file', 'Unknown')}: {result['error']}")
                    else:
                        self.stats["processed_files"] += 1
                        classification = result.get("classification", "safe")
                        self.stats["classification_results"][classification] = self.stats["classification_results"].get(classification, 0) + 1
                    
                    # Increment progress counter
                    processed_count += 1
                    
                    # Log progress
                    logging.info(f"Processed {processed_count}/{len(all_files)} files")
                    
                except queue.Empty:
                    # No results in queue yet, just continue
                    continue
                except Exception as e:
                    logging.error(f"Error processing results: {e}")
                    logging.debug(f"Exception details: {traceback.format_exc()}")
                    self.processing_error = str(e)
                    break
        
        # Finalize statistics
        self.stats["end_time"] = datetime.datetime.now().isoformat()
        processing_time = datetime.datetime.fromisoformat(self.stats["end_time"]) - datetime.datetime.fromisoformat(self.stats["start_time"])
        self.stats["processing_time_seconds"] = processing_time.total_seconds()
        
        # Log summary
        logging.info("\nProcessing Summary:")
        logging.info(f"Total files: {self.stats['total_files']}")
        logging.info(f"Successfully processed: {self.stats['processed_files']}")
        logging.info(f"Errors: {len(self.stats['errors'])}")
        logging.info(f"Time taken: {processing_time}")
        
        if self.stats["classification_results"]:
            logging.info("\nClassification Results:")
            for classification, count in sorted(self.stats["classification_results"].items()):
                logging.info(f"  {classification}: {count} files")
        
        return self.stats