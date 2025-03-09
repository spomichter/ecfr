#!/usr/bin/env python3
"""
Script to download bulk eCFR data from govinfo.gov.
This script fetches the XML data for all titles of the Code of Federal Regulations
from the govinfo.gov bulk data repository.
"""

import os
import requests
import logging
from tqdm import tqdm
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://www.govinfo.gov/bulkdata/ECFR"
OUTPUT_DIR = "../data/bulk"
MAX_WORKERS = 5  # Number of concurrent downloads

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def get_title_urls():
    """Get the list of title URLs from the govinfo.gov bulk data repository."""
    logger.info(f"Getting title URLs from: {BASE_URL}")
    
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links to title directories
        title_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('title-'):
                title_links.append({
                    'title': href,
                    'url': f"{BASE_URL}/{href}"
                })
        
        logger.info(f"Found {len(title_links)} title directories")
        return title_links
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting title URLs: {e}")
        return []

def download_file(url, output_path):
    """Download a file from a URL to a local path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get the total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download the file with progress bar
        with open(output_path, 'wb') as f, tqdm(
            desc=os.path.basename(output_path),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        
        logger.info(f"Successfully downloaded: {output_path}")
        return True
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        return False

def get_xml_files_for_title(title_url, title_name):
    """Get the list of XML files for a specific title."""
    logger.info(f"Getting XML files for title: {title_name}")
    
    try:
        response = requests.get(title_url)
        response.raise_for_status()
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links to XML files
        xml_files = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.endswith('.xml'):
                xml_files.append({
                    'filename': href,
                    'url': f"{title_url}/{href}"
                })
        
        logger.info(f"Found {len(xml_files)} XML files for title: {title_name}")
        return xml_files
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting XML files for title {title_name}: {e}")
        return []

def download_title_data(title):
    """Download all XML files for a specific title."""
    title_name = title['title']
    title_url = title['url']
    
    # Create directory for the title
    title_dir = os.path.join(OUTPUT_DIR, title_name)
    ensure_directory_exists(title_dir)
    
    # Get the list of XML files for the title
    xml_files = get_xml_files_for_title(title_url, title_name)
    
    # Download each XML file
    successful_downloads = 0
    for xml_file in xml_files:
        output_path = os.path.join(title_dir, xml_file['filename'])
        if download_file(xml_file['url'], output_path):
            successful_downloads += 1
    
    logger.info(f"Successfully downloaded {successful_downloads} out of {len(xml_files)} XML files for title: {title_name}")
    return {
        'title': title_name,
        'total_files': len(xml_files),
        'successful_downloads': successful_downloads
    }

def download_all_titles(max_titles=None):
    """Download XML data for all titles or a subset of titles."""
    # Ensure output directory exists
    ensure_directory_exists(OUTPUT_DIR)
    
    # Get the list of title URLs
    title_urls = get_title_urls()
    
    if not title_urls:
        logger.error("No title URLs found. Exiting.")
        return
    
    # Limit the number of titles if specified
    if max_titles:
        title_urls = title_urls[:max_titles]
        logger.info(f"Limiting download to first {max_titles} titles")
    
    # Download data for each title in parallel
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_title = {executor.submit(download_title_data, title): title for title in title_urls}
        for future in tqdm(as_completed(future_to_title), total=len(future_to_title), desc="Downloading titles"):
            title = future_to_title[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error downloading title {title['title']}: {e}")
    
    # Log summary
    total_files = sum(result['total_files'] for result in results)
    total_downloads = sum(result['successful_downloads'] for result in results)
    logger.info(f"Download summary: Successfully downloaded {total_downloads} out of {total_files} XML files for {len(results)} titles")
    
    return results

if __name__ == "__main__":
    # By default, download all titles
    # Uncomment and modify the line below to limit the number of titles for testing
    # download_all_titles(max_titles=3)
    download_all_titles()
