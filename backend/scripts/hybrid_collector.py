#!/usr/bin/env python3
"""
Script to implement a hybrid approach for collecting eCFR data.
This script combines API calls for metadata with web scraping for content.
"""

import os
import json
import logging
import time
from datetime import datetime
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://www.ecfr.gov"
API_BASE_URL = "https://www.ecfr.gov"
AGENCIES_ENDPOINT = "/api/admin/v1/agencies.json"
TITLES_ENDPOINT = "/api/versioner/v1/titles.json"
BROWSE_URL = "https://www.ecfr.gov/current/title-{title}"
OUTPUT_DIR = "../data/hybrid"

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def get_agencies():
    """Get the list of agencies from the eCFR API."""
    url = f"{API_BASE_URL}{AGENCIES_ENDPOINT}"
    logger.info(f"Getting agencies from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the JSON response
        agencies_data = response.json()
        
        # Create timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        agencies_dir = os.path.join(OUTPUT_DIR, "agencies")
        ensure_directory_exists(agencies_dir)
        
        # Save the raw JSON data
        output_file = os.path.join(agencies_dir, f"agencies_{timestamp}.json")
        with open(output_file, 'w') as f:
            json.dump(agencies_data, f, indent=2)
        
        logger.info(f"Successfully saved agencies data to: {output_file}")
        
        # Also save a copy as latest.json for easy access
        latest_file = os.path.join(agencies_dir, "latest.json")
        with open(latest_file, 'w') as f:
            json.dump(agencies_data, f, indent=2)
        
        logger.info(f"Successfully saved latest agencies data to: {latest_file}")
        
        # Count agencies
        agency_count = len(agencies_data.get("agencies", []))
        logger.info(f"Downloaded information for {agency_count} agencies")
        
        return agencies_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading agencies data: {e}")
        return None

def get_titles():
    """Get the list of titles from the eCFR API."""
    url = f"{API_BASE_URL}{TITLES_ENDPOINT}"
    logger.info(f"Getting titles from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the JSON response
        titles_data = response.json()
        
        # Create timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        titles_dir = os.path.join(OUTPUT_DIR, "titles")
        ensure_directory_exists(titles_dir)
        
        # Save the raw JSON data
        output_file = os.path.join(titles_dir, f"titles_{timestamp}.json")
        with open(output_file, 'w') as f:
            json.dump(titles_data, f, indent=2)
        
        logger.info(f"Successfully saved titles data to: {output_file}")
        
        # Also save a copy as latest.json for easy access
        latest_file = os.path.join(titles_dir, "latest.json")
        with open(latest_file, 'w') as f:
            json.dump(titles_data, f, indent=2)
        
        logger.info(f"Successfully saved latest titles data to: {latest_file}")
        
        # Count titles
        title_count = len(titles_data.get("titles", []))
        logger.info(f"Downloaded information for {title_count} titles")
        
        return titles_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading titles data: {e}")
        return None

def scrape_title_structure(title_number, title_name):
    """Scrape the structure of a specific title."""
    title_url = BROWSE_URL.format(title=title_number)
    logger.info(f"Scraping structure for Title {title_number}: {title_name} from {title_url}")
    
    title_dir = os.path.join(OUTPUT_DIR, "content", f"title_{title_number}")
    ensure_directory_exists(title_dir)
    
    try:
        # Get the title page
        response = requests.get(title_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the structure
        structure = {
            "title": title_number,
            "name": title_name,
            "url": title_url,
            "chapters": []
        }
        
        # Find all chapter elements
        chapter_elements = soup.find_all('a', string=lambda s: s and s.startswith('Chapter'))
        
        for chapter_elem in chapter_elements:
            chapter_text = chapter_elem.get_text(strip=True)
            chapter_match = re.search(r'Chapter\s+([IVXLCDMivxlcdm]+)', chapter_text)
            
            if chapter_match:
                chapter_num = chapter_match.group(1)
                
                # Find the next element which should contain the chapter name
                chapter_name_elem = chapter_elem.find_next()
                chapter_name = chapter_name_elem.get_text(strip=True) if chapter_name_elem else ""
                
                # Find the parts range
                parts_range_elem = chapter_elem.find_next('a')
                parts_range = parts_range_elem.get_text(strip=True) if parts_range_elem else ""
                
                # Find the table that follows this chapter heading
                table = chapter_elem.find_next('table')
                parts = []
                
                if table:
                    # Extract parts from the table
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            part_elem = cells[0].find('a')
                            if part_elem and 'Part' in part_elem.get_text(strip=True):
                                part_text = part_elem.get_text(strip=True)
                                part_match = re.search(r'Part\s+(\d+)', part_text)
                                
                                if part_match:
                                    part_num = part_match.group(1)
                                    part_name = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                                    part_sections = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                                    
                                    part_info = {
                                        "part": part_num,
                                        "name": part_name,
                                        "sections": part_sections,
                                        "url": f"{BASE_URL}/current/title-{title_number}/part-{part_num}"
                                    }
                                    
                                    parts.append(part_info)
                
                chapter_info = {
                    "chapter": chapter_num,
                    "name": chapter_name,
                    "parts_range": parts_range,
                    "parts": parts
                }
                
                structure["chapters"].append(chapter_info)
        
        # Save the structure
        structure_file = os.path.join(title_dir, f"structure_{title_number}.json")
        with open(structure_file, 'w') as f:
            json.dump(structure, f, indent=2)
        
        logger.info(f"Successfully saved structure to: {structure_file}")
        
        # Save the HTML for reference
        html_file = os.path.join(title_dir, f"title_{title_number}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logger.info(f"Successfully saved HTML to: {html_file}")
        
        return structure
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping structure for Title {title_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scraping structure for Title {title_number}: {e}")
        return None

def scrape_part_content(title_number, part_number, part_name):
    """Scrape content for a specific part."""
    part_url = f"{BASE_URL}/current/title-{title_number}/part-{part_number}"
    logger.info(f"Scraping content for Title {title_number}, Part {part_number}: {part_name} from {part_url}")
    
    part_dir = os.path.join(OUTPUT_DIR, "content", f"title_{title_number}", f"part_{part_number}")
    ensure_directory_exists(part_dir)
    
    try:
        # Get the part page
        response = requests.get(part_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save the HTML for reference
        html_file = os.path.join(part_dir, f"part_{part_number}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logger.info(f"Successfully saved HTML to: {html_file}")
        
        # Extract text content
        main_content = soup.find('main')
        if main_content:
            text_content = main_content.get_text(separator='\n', strip=True)
            
            # Save the text content
            text_file = os.path.join(part_dir, f"part_{part_number}.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"Successfully saved text content to: {text_file}")
        else:
            logger.warning(f"Could not find main content for Title {title_number}, Part {part_number}")
        
        # Extract sections
        sections = []
        section_elements = soup.find_all('h3', class_=lambda c: c and 'section-heading' in c)
        
        for section_elem in section_elements:
            section_text = section_elem.get_text(strip=True)
            section_match = re.search(r'§\s+(\d+\.\d+)', section_text)
            
            if section_match:
                section_num = section_match.group(1)
                section_title = section_text.replace(f"§ {section_num}", "").strip()
                
                # Find the content that follows this section heading
                section_content = ""
                next_elem = section_elem.find_next_sibling()
                while next_elem and not (next_elem.name == 'h3' and next_elem.get('class') and 'section-heading' in next_elem.get('class')):
                    section_content += next_elem.get_text(strip=True) + "\n"
                    next_elem = next_elem.find_next_sibling()
                
                section_info = {
                    "section": section_num,
                    "title": section_title,
                    "content": section_content.strip()
                }
                
                sections.append(section_info)
        
        # Save the sections
        sections_file = os.path.join(part_dir, f"sections_{part_number}.json")
        with open(sections_file, 'w') as f:
            json.dump(sections, f, indent=2)
        
        logger.info(f"Successfully saved {len(sections)} sections to: {sections_file}")
        
        return {
            "html_file": html_file,
            "sections_file": sections_file,
            "section_count": len(sections)
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping content for Title {title_number}, Part {part_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scraping content for Title {title_number}, Part {part_number}: {e}")
        return None

def collect_data(max_titles=None, max_parts_per_title=None):
    """Collect data using a hybrid approach of API calls and web scraping."""
    # Ensure output directory exists
    ensure_directory_exists(OUTPUT_DIR)
    
    # Create timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Step 1: Get agencies data from API
    agencies_data = get_agencies()
    
    # Step 2: Get titles data from API
    titles_data = get_titles()
    
    if not titles_data:
        logger.error("No titles data found. Exiting.")
        return
    
    titles = titles_data.get("titles", [])
    
    # Limit the number of titles if specified
    if max_titles:
        titles = titles[:max_titles]
        logger.info(f"Limiting collection to first {max_titles} titles")
    
    # Step 3: Scrape structure and content for each title
    title_results = {}
    for title in tqdm(titles, desc="Processing titles"):
        title_number = title.get("number")
        title_name = title.get("name")
        
        logger.info(f"Processing Title {title_number}: {title_name}")
        
        # Scrape title structure
        structure = scrape_title_structure(title_number, title_name)
        
        if structure:
            part_results = {}
            
            # Scrape content for each part
            parts = []
            for chapter in structure.get("chapters", []):
                parts.extend(chapter.get("parts", []))
            
            # Limit the number of parts if specified
            if max_parts_per_title:
                parts = parts[:max_parts_per_title]
                logger.info(f"Limiting to first {max_parts_per_title} parts for Title {title_number}")
            
            for part in tqdm(parts, desc=f"Processing parts for Title {title_number}"):
                part_number = part.get("part")
                part_name = part.get("name")
                
                result = scrape_part_content(title_number, part_number, part_name)
                if result:
                    part_results[part_number] = result
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(1)
            
            title_results[title_number] = {
                "name": title_name,
                "structure": structure,
                "parts": part_results
            }
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(2)
    
    # Save the summary
    summary_file = os.path.join(OUTPUT_DIR, f"collection_summary_{timestamp}.json")
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "total_titles": len(titles),
            "successful_titles": len(title_results),
            "results": title_results
        }, f, indent=2)
    
    logger.info(f"Collection summary saved to: {summary_file}")
    logger.info(f"Successfully processed {len(title_results)} out of {len(titles)} titles")
    
    return {
        "agencies": agencies_data,
        "titles": titles_data,
        "content": title_results
    }

if __name__ == "__main__":
    # By default, collect data for all titles
    # Uncomment and modify the lines below to limit the collection for testing
    # collect_data(max_titles=3, max_parts_per_title=5)
    collect_data()
