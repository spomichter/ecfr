#!/usr/bin/env python3
"""
Script to download regulation content from the eCFR API.
This script fetches the full content of regulations by title from the eCFR API
and saves it to XML files for further processing.
"""

import os
import json
import requests
import xmltodict
from datetime import datetime
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://www.ecfr.gov"
TITLES_ENDPOINT = "/api/versioner/v1/titles.json"
FULL_CONTENT_ENDPOINT = "/api/versioner/v1/full/{date}/title-{title}.xml"
STRUCTURE_ENDPOINT = "/api/versioner/v1/structure/{date}/title-{title}.json"
VERSIONS_ENDPOINT = "/api/versioner/v1/versions/title-{title}.json"
OUTPUT_DIR = "../data/regulations"

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def get_titles():
    """Get the list of titles from the eCFR API."""
    url = f"{BASE_URL}{TITLES_ENDPOINT}"
    logger.info(f"Getting titles from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("titles", [])
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting titles: {e}")
        return []

def get_current_date():
    """Get the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def download_regulation_content(title_number, date=None):
    """Download full regulation content for a specific title."""
    if date is None:
        date = get_current_date()
        
    title_dir = os.path.join(OUTPUT_DIR, f"title_{title_number}")
    ensure_directory_exists(title_dir)
    
    # Download full content (XML)
    full_url = f"{BASE_URL}{FULL_CONTENT_ENDPOINT.format(date=date, title=title_number)}"
    logger.info(f"Downloading full content for Title {title_number} from: {full_url}")
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        
        # Save the XML content
        xml_file = os.path.join(title_dir, f"title_{title_number}_{date}.xml")
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logger.info(f"Successfully saved XML content to: {xml_file}")
        
        # Also save as latest.xml for easy access
        latest_xml = os.path.join(title_dir, "latest.xml")
        with open(latest_xml, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Download structure (JSON)
        structure_url = f"{BASE_URL}{STRUCTURE_ENDPOINT.format(date=date, title=title_number)}"
        logger.info(f"Downloading structure for Title {title_number} from: {structure_url}")
        
        structure_response = requests.get(structure_url)
        structure_response.raise_for_status()
        
        # Save the structure JSON
        structure_file = os.path.join(title_dir, f"structure_{title_number}_{date}.json")
        with open(structure_file, 'w') as f:
            json.dump(structure_response.json(), f, indent=2)
        
        logger.info(f"Successfully saved structure data to: {structure_file}")
        
        # Also save as latest_structure.json for easy access
        latest_structure = os.path.join(title_dir, "latest_structure.json")
        with open(latest_structure, 'w') as f:
            json.dump(structure_response.json(), f, indent=2)
        
        # Download versions (sections and appendices)
        versions_url = f"{BASE_URL}{VERSIONS_ENDPOINT.format(title=title_number)}"
        logger.info(f"Downloading versions for Title {title_number} from: {versions_url}")
        
        versions_response = requests.get(versions_url)
        versions_response.raise_for_status()
        
        # Save the versions JSON
        versions_file = os.path.join(title_dir, f"versions_{title_number}.json")
        with open(versions_file, 'w') as f:
            json.dump(versions_response.json(), f, indent=2)
        
        logger.info(f"Successfully saved versions data to: {versions_file}")
        
        return {
            "xml_file": xml_file,
            "structure_file": structure_file,
            "versions_file": versions_file
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading regulation content for Title {title_number}: {e}")
        return None

def download_all_regulations(max_titles=None, date=None):
    """Download regulations for all titles or a subset of titles."""
    if date is None:
        date = get_current_date()
        
    titles = get_titles()
    
    if not titles:
        logger.error("No titles found. Exiting.")
        return
    
    # Limit the number of titles if specified
    if max_titles:
        titles = titles[:max_titles]
        logger.info(f"Limiting download to first {max_titles} titles")
    
    # Create timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure output directory exists
    ensure_directory_exists(OUTPUT_DIR)
    
    # Create a summary file
    summary_file = os.path.join(OUTPUT_DIR, f"download_summary_{timestamp}.json")
    
    # Download regulations for each title
    results = {}
    for title in tqdm(titles, desc="Downloading titles"):
        title_number = title.get("number")
        title_name = title.get("name")
        
        logger.info(f"Processing Title {title_number}: {title_name}")
        
        result = download_regulation_content(title_number, date)
        if result:
            results[title_number] = {
                "name": title_name,
                "files": result
            }
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(1)
    
    # Save the summary
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "date_used": date,
            "total_titles": len(titles),
            "successful_downloads": len(results),
            "results": results
        }, f, indent=2)
    
    logger.info(f"Download summary saved to: {summary_file}")
    logger.info(f"Successfully downloaded {len(results)} out of {len(titles)} titles")
    
    return results

if __name__ == "__main__":
    # By default, download all regulations using today's date
    # Uncomment and modify the line below to limit the number of titles for testing
    # download_all_regulations(max_titles=5)
    download_all_regulations()
