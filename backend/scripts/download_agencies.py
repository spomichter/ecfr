#!/usr/bin/env python3
"""
Script to download agency information from the eCFR API.
This script fetches the list of agencies and their metadata from the eCFR API
and saves it to a JSON file for further processing.
"""

import os
import json
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://www.ecfr.gov"
AGENCIES_ENDPOINT = "/api/admin/v1/agencies.json"
OUTPUT_DIR = "../data/agencies"

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def download_agencies():
    """Download agency information from the eCFR API."""
    url = f"{BASE_URL}{AGENCIES_ENDPOINT}"
    logger.info(f"Downloading agencies from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the JSON response
        agencies_data = response.json()
        
        # Create timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        ensure_directory_exists(OUTPUT_DIR)
        
        # Save the raw JSON data
        output_file = os.path.join(OUTPUT_DIR, f"agencies_{timestamp}.json")
        with open(output_file, 'w') as f:
            json.dump(agencies_data, f, indent=2)
        
        logger.info(f"Successfully saved agencies data to: {output_file}")
        
        # Also save a copy as latest.json for easy access
        latest_file = os.path.join(OUTPUT_DIR, "latest.json")
        with open(latest_file, 'w') as f:
            json.dump(agencies_data, f, indent=2)
        
        logger.info(f"Successfully saved latest agencies data to: {latest_file}")
        
        # Count agencies
        agency_count = len(agencies_data.get("agencies", []))
        logger.info(f"Downloaded information for {agency_count} agencies")
        
        return output_file
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading agencies data: {e}")
        return None

if __name__ == "__main__":
    download_agencies()
