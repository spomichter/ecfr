#!/usr/bin/env python3
"""
Script to improve data collection for eCFR content.
This script uses a more comprehensive approach to scrape regulation content from the eCFR website.
"""

import os
import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from tqdm import tqdm
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)
print("Starting improved eCFR content collection script")

# Constants
BASE_URL = "https://www.ecfr.gov"
TITLES_ENDPOINT = "/api/versioner/v1/titles.json"
OUTPUT_DIR = "../data/improved_content"
MAX_WORKERS = 4  # Number of concurrent requests

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")
        print(f"Created directory: {directory}")

def get_titles():
    """Get the list of titles from the eCFR API."""
    url = f"{BASE_URL}{TITLES_ENDPOINT}"
    logger.info(f"Getting titles from: {url}")
    print(f"Getting titles from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        titles = response.json().get("titles", [])
        logger.info(f"Retrieved {len(titles)} titles")
        print(f"Retrieved {len(titles)} titles")
        return titles
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting titles: {e}")
        print(f"Error getting titles: {e}")
        return []

def get_title_parts(title_number):
    """Get the list of parts for a specific title."""
    title_url = f"{BASE_URL}/current/title-{title_number}"
    logger.info(f"Getting parts for Title {title_number} from: {title_url}")
    print(f"Getting parts for Title {title_number} from: {title_url}")
    
    try:
        response = requests.get(title_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all part links
        part_links = []
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and '/current/title-' in href and '/part-' in href:
                part_match = re.search(r'/current/title-(\d+)/part-(\d+)', href)
                if part_match and part_match.group(1) == str(title_number):
                    part_number = part_match.group(2)
                    part_links.append({
                        'title': title_number,
                        'part': part_number,
                        'url': href if href.startswith('http') else f"{BASE_URL}{href}"
                    })
        
        logger.info(f"Found {len(part_links)} parts for Title {title_number}")
        print(f"Found {len(part_links)} parts for Title {title_number}")
        return part_links
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting parts for Title {title_number}: {e}")
        print(f"Error getting parts for Title {title_number}: {e}")
        return []

def get_part_sections(part_url):
    """Get the list of sections for a specific part."""
    logger.info(f"Getting sections from: {part_url}")
    print(f"Getting sections from: {part_url}")
    
    try:
        response = requests.get(part_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title and part numbers from URL
        url_match = re.search(r'/current/title-(\d+)/part-(\d+)', part_url)
        if not url_match:
            logger.error(f"Could not extract title and part numbers from URL: {part_url}")
            print(f"Could not extract title and part numbers from URL: {part_url}")
            return None
        
        title_number = url_match.group(1)
        part_number = url_match.group(2)
        
        # Find the part title
        part_title_elem = soup.find('h1')
        part_title = part_title_elem.get_text(strip=True) if part_title_elem else f"Part {part_number}"
        
        # Find all section headings
        sections = []
        section_headings = soup.find_all('h3', class_=lambda c: c and 'section-heading' in c)
        
        for heading in section_headings:
            section_text = heading.get_text(strip=True)
            section_match = re.search(r'§\s+(\d+\.\d+)', section_text)
            
            if section_match:
                section_number = section_match.group(1)
                section_title = section_text.replace(f"§ {section_number}", "").strip()
                
                # Find the content that follows this section heading
                section_content = ""
                next_elem = heading.find_next_sibling()
                while next_elem and not (next_elem.name == 'h3' and next_elem.get('class') and 'section-heading' in next_elem.get('class')):
                    if next_elem.name in ['p', 'div']:
                        section_content += next_elem.get_text(strip=True) + "\n\n"
                    next_elem = next_elem.find_next_sibling()
                
                sections.append({
                    'section_number': section_number,
                    'section_title': section_title,
                    'content': section_content.strip()
                })
        
        # Create the part data structure
        part_data = {
            'title_number': title_number,
            'part_number': part_number,
            'part_title': part_title,
            'url': part_url,
            'sections': sections
        }
        
        logger.info(f"Found {len(sections)} sections for Title {title_number}, Part {part_number}")
        print(f"Found {len(sections)} sections for Title {title_number}, Part {part_number}")
        return part_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting sections from {part_url}: {e}")
        print(f"Error getting sections from {part_url}: {e}")
        return None

def process_title(title):
    """Process a title to collect all its parts and sections."""
    title_number = title.get("number")
    title_name = title.get("name")
    
    logger.info(f"Processing Title {title_number}: {title_name}")
    print(f"Processing Title {title_number}: {title_name}")
    
    # Create directory for this title
    title_dir = os.path.join(OUTPUT_DIR, f"title_{title_number}")
    ensure_directory_exists(title_dir)
    
    # Get parts for this title
    parts = get_title_parts(title_number)
    
    # Save parts list
    parts_file = os.path.join(title_dir, "parts.json")
    with open(parts_file, 'w') as f:
        json.dump(parts, f, indent=2)
    
    # Process each part
    part_data_list = []
    
    # Use ThreadPoolExecutor for concurrent processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks
        future_to_part = {executor.submit(get_part_sections, part['url']): part for part in parts}
        
        # Process results as they complete
        for future in tqdm(concurrent.futures.as_completed(future_to_part), total=len(parts), desc=f"Processing parts for Title {title_number}"):
            part = future_to_part[future]
            try:
                part_data = future.result()
                if part_data:
                    part_data_list.append(part_data)
                    
                    # Save individual part data
                    part_file = os.path.join(title_dir, f"part_{part['part']}.json")
                    with open(part_file, 'w') as f:
                        json.dump(part_data, f, indent=2)
            except Exception as e:
                logger.error(f"Error processing part {part['part']} of Title {title_number}: {e}")
                print(f"Error processing part {part['part']} of Title {title_number}: {e}")
    
    # Save all parts data for this title
    all_parts_file = os.path.join(title_dir, "all_parts.json")
    with open(all_parts_file, 'w') as f:
        json.dump(part_data_list, f, indent=2)
    
    # Create a title summary
    title_summary = {
        'title_number': title_number,
        'title_name': title_name,
        'part_count': len(parts),
        'collected_parts': len(part_data_list),
        'section_count': sum(len(part_data['sections']) for part_data in part_data_list),
        'parts': parts
    }
    
    # Save title summary
    summary_file = os.path.join(title_dir, "summary.json")
    with open(summary_file, 'w') as f:
        json.dump(title_summary, f, indent=2)
    
    logger.info(f"Completed processing Title {title_number}: collected {len(part_data_list)} parts with {title_summary['section_count']} sections")
    print(f"Completed processing Title {title_number}: collected {len(part_data_list)} parts with {title_summary['section_count']} sections")
    
    return title_summary

def collect_improved_content(max_titles=None):
    """Collect improved content from the eCFR website."""
    # Ensure output directory exists
    ensure_directory_exists(OUTPUT_DIR)
    
    # Get titles
    titles = get_titles()
    
    if not titles:
        logger.error("No titles found. Exiting.")
        print("No titles found. Exiting.")
        return
    
    # Limit the number of titles if specified
    if max_titles:
        titles = titles[:max_titles]
        logger.info(f"Limiting collection to first {max_titles} titles")
        print(f"Limiting collection to first {max_titles} titles")
    
    # Create timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Process each title
    title_summaries = []
    for title in tqdm(titles, desc="Processing titles"):
        title_summary = process_title(title)
        if title_summary:
            title_summaries.append(title_summary)
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
    
    # Create overall summary
    overall_summary = {
        'timestamp': timestamp,
        'total_titles': len(titles),
        'processed_titles': len(title_summaries),
        'total_parts': sum(summary['part_count'] for summary in title_summaries),
        'collected_parts': sum(summary['collected_parts'] for summary in title_summaries),
        'total_sections': sum(summary['section_count'] for summary in title_summaries),
        'title_summaries': title_summaries
    }
    
    # Save overall summary
    summary_file = os.path.join(OUTPUT_DIR, f"collection_summary_{timestamp}.json")
    with open(summary_file, 'w') as f:
        json.dump(overall_summary, f, indent=2)
    
    # Also save as latest.json for easy access
    latest_file = os.path.join(OUTPUT_DIR, "latest.json")
    with open(latest_file, 'w') as f:
        json.dump(overall_summary, f, indent=2)
    
    logger.info(f"Collection summary saved to: {summary_file}")
    print(f"Collection summary saved to: {summary_file}")
    logger.info(f"Successfully processed {len(title_summaries)} out of {len(titles)} titles")
    print(f"Successfully processed {len(title_summaries)} out of {len(titles)} titles")
    logger.info(f"Collected {overall_summary['collected_parts']} parts with {overall_summary['total_sections']} sections")
    print(f"Collected {overall_summary['collected_parts']} parts with {overall_summary['total_sections']} sections")
    
    return overall_summary

if __name__ == "__main__":
    print("Script execution started")
    # Collect improved content
    # Uncomment and modify the line below to limit the number of titles for testing
    collect_improved_content(max_titles=3)
    # collect_improved_content()
    print("Script execution completed")
