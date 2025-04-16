import requests
import logging
import time
import threading
import traceback
from typing import Dict, List, Any, Optional

class ClassiAPI:
    """Client for the Data443.Classi.WebApi with rate limiting."""
    
    def __init__(self, base_url: str = "https://classiapi.data443.com", max_requests_per_minute: int = 60):
        self.base_url = base_url.rstrip('/')
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = []
        self.lock = threading.Lock()
        self.policies_cache = None
        self.policy_cache = {}
        logging.debug(f"Initialized ClassiAPI with base URL: {self.base_url}")
        logging.debug(f"Rate limit set to {max_requests_per_minute} requests per minute")
        
    def _wait_for_rate_limit(self):
        """Wait if necessary to comply with rate limit."""
        with self.lock:
            current_time = time.time()
            
            # Remove request times older than 60 seconds
            self.request_times = [t for t in self.request_times if current_time - t < 60]
            
            # Check if we've hit the rate limit
            if len(self.request_times) >= self.max_requests_per_minute:
                # Calculate time to wait
                oldest_time = min(self.request_times)
                wait_time = 60 - (current_time - oldest_time)
                if wait_time > 0:
                    logging.debug(f"Rate limit reached. Waiting {wait_time:.2f} seconds before next request.")
                    time.sleep(wait_time)
            
            # Add current request time
            self.request_times.append(time.time())
    
    def classify_text(self, text: str, policy_id: str) -> Dict[str, Any]:
        """Classify text against a policy with rate limiting."""
        self._wait_for_rate_limit()
        
        # Skip empty text to avoid unnecessary API calls
        if not text or len(text.strip()) == 0:
            logging.debug("Empty text provided, skipping API call")
            return {"totalMatches": 0, "matches": []}
            
        endpoint = f"{self.base_url}/api/classification/text"
        files = {
            'Text': (None, text),
            'PolicyId': (None, policy_id)
        }
        
        logging.debug(f"Calling classification API for policy {policy_id}")
        logging.debug(f"Text length: {len(text)} characters")
        
        try:
            response = requests.post(endpoint, files=files)
            response.raise_for_status()
            result = response.json()
            
            # Log detailed response information
            logging.debug(f"Classification response status: {response.status_code}")
            logging.debug(f"Classification matches: {result['totalMatches']}")
            if result['totalMatches'] > 0:
                for match in result['matches']:
                    logging.debug(f"Match: {match['name']} (ID: {match['id']}, Confidence: {match['confidence']})")
            
            return result
        except Exception as e:
            logging.error(f"Error in classify_text: {str(e)}")
            logging.debug(f"Exception details: {traceback.format_exc()}")
            raise
    
    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all available policies with caching."""
        # Check if we have cached policies
        if self.policies_cache is not None:
            logging.debug("Using cached policies")
            return self.policies_cache
        
        self._wait_for_rate_limit()
        endpoint = f"{self.base_url}/api/policies"
        
        logging.debug(f"Retrieving policies from {endpoint}")
        
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            policies = response.json()
            
            logging.debug(f"Retrieved {len(policies)} policies")
            for policy in policies:
                logging.debug(f"Policy: {policy['name']} (ID: {policy['id']})")
            
            # Cache the policies
            self.policies_cache = policies
            return policies
        except Exception as e:
            logging.error(f"Error in get_policies: {str(e)}")
            logging.debug(f"Exception details: {traceback.format_exc()}")
            raise
    
    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get details for a specific policy with caching."""
        # Check if we have cached this policy
        if policy_id in self.policy_cache:
            logging.debug(f"Using cached policy for ID: {policy_id}")
            return self.policy_cache[policy_id]
        
        self._wait_for_rate_limit()
        endpoint = f"{self.base_url}/api/policies/{policy_id}"
        
        logging.debug(f"Retrieving policy details for ID: {policy_id}")
        
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            policy = response.json()
            
            logging.debug(f"Retrieved policy: {policy['name']} (ID: {policy['id']})")
            
            # Cache the policy
            self.policy_cache[policy_id] = policy
            return policy
        except Exception as e:
            logging.error(f"Error in get_policy: {str(e)}")
            logging.debug(f"Exception details: {traceback.format_exc()}")
            raise