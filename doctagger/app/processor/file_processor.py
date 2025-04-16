# File processor module
import logging
import datetime
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

from ..api.classi_client import ClassiAPI
from ..reader.reader_factory import ReaderFactory
from ..tagger.tagger_factory import TaggerFactory

def process_file(file_path: Path, api: ClassiAPI, tag_name: str, no_tag: bool, use_first_match: bool = False) -> Dict[str, Any]:
    """Process a single file.
    
    Args:
        file_path: Path to the file to process
        api: ClassiAPI instance
        tag_name: Name of the tag to add to the document
        no_tag: If True, skip tagging
        use_first_match: If True, use the first match instead of highest confidence
    
    Returns a dictionary with information about the processing result.
    """
    result = {
        "file": str(file_path),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    logging.info(f"\nProcessing file: {file_path}")
    logging.debug(f"File size: {file_path.stat().st_size} bytes")
    
    try:
        # Get the appropriate reader for the file type
        reader = ReaderFactory.get_reader(file_path)
        
        # Read the document content
        logging.debug(f"Reading document content")
        try:
            document_text = reader.read_document(file_path)
            if not document_text or len(document_text.strip()) == 0:
                logging.warning(f"Extracted text is empty. The file may not contain readable text or may be corrupted.")
                result["error"] = "Document contains no readable text"
                result["classification"] = "unknown"
                return result
                
            logging.debug(f"Successfully read {len(document_text)} characters")
            result["text_length"] = len(document_text)
            
            # Add a small excerpt for debugging (first 100 chars)
            try:
                # Clean excerpt for console display to avoid encoding errors
                excerpt = document_text[:100].replace('\n', ' ')
                excerpt = ''.join(ch if ord(ch) < 0x10000 else '?' for ch in excerpt)
                logging.debug(f"Document excerpt: {excerpt}...")
            except Exception as excerpt_error:
                logging.debug(f"Error creating excerpt: {excerpt_error}")
        except Exception as read_error:
            logging.error(f"Failed to read document: {read_error}")
            result["error"] = f"Failed to read document: {str(read_error)}"
            result["classification"] = "unknown"
            return result
        
        # Get policies
        policies = api.get_policies()
        logging.debug(f"Retrieved {len(policies)} policies")
        
        # Create a list to store all matches
        all_matches = []
        
        # Check document against policies
        for policy in policies:
            try:
                classification_result = api.classify_text(document_text, policy['id'])
                
                if classification_result['totalMatches'] > 0:
                    # Get the highest confidence match
                    highest_match = max(classification_result['matches'], key=lambda x: x['confidence'])
                    
                    match_info = {
                        'policy_id': policy['id'],
                        'policy_name': policy['name'],
                        'match_id': highest_match['id'],
                        'match_name': highest_match['name'],
                        'confidence': highest_match['confidence'],
                        'total_matches': classification_result['totalMatches']
                    }
                    
                    all_matches.append(match_info)
                    logging.info(f"  Match found: {match_info['match_name']} (Confidence: {match_info['confidence']})")
                    
                    # Stop after first match if requested
                    if use_first_match:
                        break
                else:
                    logging.debug(f"  No matches found for policy: {policy['name']}")
            except Exception as e:
                error_msg = f"Error checking policy {policy['name']}: {str(e)}"
                logging.error(error_msg)
                logging.debug(f"Exception details: {traceback.format_exc()}")
        
        # Determine classification result and store matches
        result["matches"] = all_matches
        result["matches_count"] = len(all_matches)
        
        if all_matches:
            if use_first_match:
                # Use the first match found
                classification = all_matches[0]['policy_name']
                confidence = all_matches[0]['confidence']
                logging.info(f"\nUsing first match found (--first option): {classification} (Confidence: {confidence})")
            else:
                # Sort matches by confidence (highest first)
                all_matches.sort(key=lambda x: x['confidence'], reverse=True)
                
                # Get the highest confidence match
                top_match = all_matches[0]
                classification = top_match['policy_name']
                confidence = top_match['confidence']
                
                logging.info("\nMatching policies (ordered by confidence):")
                for idx, match in enumerate(all_matches, 1):
                    logging.info(f"  {idx}. {match['policy_name']} (Confidence: {match['confidence']})")
                
                logging.info(f"\nHighest confidence match: {classification}")
            
            result["classification"] = classification
            result["confidence"] = confidence
        else:
            classification = "safe"
            logging.info("\nNo policy matches found, classified as: safe")
            result["classification"] = classification
        
        # Tag the document
        if not no_tag:
            logging.info(f"Tagging document with: {tag_name}={classification}")
            tagger = TaggerFactory.get_tagger(file_path)
            tag_success = tagger.tag_document(file_path, tag_name, classification)
            result["tagged"] = tag_success
            
            if not tag_success:
                logging.warning("Warning: Unable to tag document. Check if the file format is supported.")
        else:
            logging.info("Skipping document tagging as requested")
            result["tagged"] = False
        
        return result
        
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        logging.error(error_msg)
        logging.debug(f"Exception details: {traceback.format_exc()}")
        return {"error": error_msg, "file": str(file_path)}