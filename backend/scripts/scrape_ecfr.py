#!/usr/bin/env python3
"""
Script to scrape eCFR content from the website.
This script uses BeautifulSoup to navigate the eCFR website and extract regulation content.
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
BROWSE_URL = "https://www.ecfr.gov/current/title-{title}"
OUTPUT_DIR = "../data/scraped"

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def get_titles():
    """Get the list of titles from the eCFR API."""
    url = f"{BASE_URL}/api/versioner/v1/titles.json"
    logger.info(f"Getting titles from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("titles", [])
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting titles: {e}")
        return []

def scrape_title_content(title_number, title_name):
    """Scrape content for a specific title."""
    title_url = BROWSE_URL.format(title=title_number)
    logger.info(f"Scraping content for Title {title_number}: {title_name} from {title_url}")
    
    title_dir = os.path.join(OUTPUT_DIR, f"title_{title_number}")
    ensure_directory_exists(title_dir)
    
    try:
        # Get the title page
        response = requests.get(title_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the content - based on actual page structure
        content_div = soup.find('div', id='ecfr-content')
        if not content_div:
            logger.error(f"Could not find content div for Title {title_number}")
            return None
        
        # Save the HTML content
        html_file = os.path.join(title_dir, f"title_{title_number}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(content_div))
        
        logger.info(f"Saved HTML content to {html_file}")
        
        # Extract text content
        text_content = content_div.get_text(separator='\n', strip=True)
        
        # Save the text content
        text_file = os.path.join(title_dir, f"title_{title_number}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        logger.info(f"Saved text content to {text_file}")
        
        # Extract structure
        structure = extract_structure(soup, title_number)
        
        # Save the structure
        structure_file = os.path.join(title_dir, f"structure_{title_number}.json")
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2)
        
        logger.info(f"Saved structure to {structure_file}")
        
        # Extract chapters and parts
        chapters = extract_chapters(soup)
        
        # Save chapters information
        chapters_file = os.path.join(title_dir, f"chapters_{title_number}.json")
        with open(chapters_file, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, indent=2)
        
        logger.info(f"Saved chapters information to {chapters_file}")
        
        return {
            "html_file": html_file,
            "text_file": text_file,
            "structure_file": structure_file,
            "chapters_file": chapters_file
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping content for Title {title_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scraping content for Title {title_number}: {e}")
        return None

def extract_structure(soup, title_number):
    """Extract the structure from the title page."""
    structure = {
        "title": title_number,
        "name": soup.find('h1').get_text(strip=True) if soup.find('h1') else f"Title {title_number}",
        "chapters": []
    }
    
    # Find all chapter links
    chapter_links = soup.find_all('a', string=lambda s: s and s.startswith('Chapter'))
    
    for chapter_link in chapter_links:
        chapter_text = chapter_link.get_text(strip=True)
        chapter_match = re.search(r'Chapter\s+([IVXLCDMivxlcdm]+)', chapter_text)
        
        if chapter_match:
            chapter_num = chapter_match.group(1)
            
            # Find the next element which should contain the chapter name
            chapter_name_elem = chapter_link.find_next()
            chapter_name = chapter_name_elem.get_text(strip=True) if chapter_name_elem else ""
            
            # Find the parts range
            parts_range_elem = chapter_link.find_next('a')
            parts_range = parts_range_elem.get_text(strip=True) if parts_range_elem else ""
            
            chapter_info = {
                "chapter": chapter_num,
                "name": chapter_name,
                "parts_range": parts_range,
                "parts": []
            }
            
            structure["chapters"].append(chapter_info)
    
    return structure

def extract_chapters(soup):
    """Extract chapters and their parts from the title page."""
    chapters = []
    
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
            
            chapters.append(chapter_info)
    
    return chapters

def scrape_part_content(title_number, part_number):
    """Scrape content for a specific part."""
    part_url = f"{BASE_URL}/current/title-{title_number}/part-{part_number}"
    logger.info(f"Scraping content for Title {title_number}, Part {part_number} from {part_url}")
    
    part_dir = os.path.join(OUTPUT_DIR, f"title_{title_number}", f"part_{part_number}")
    ensure_directory_exists(part_dir)
    
    try:
        # Get the part page
        response = requests.get(part_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the content
        content_div = soup.find('div', id='ecfr-content')
        if not content_div:
            logger.error(f"Could not find content div for Title {title_number}, Part {part_number}")
            return None
        
        # Save the HTML content
        html_file = os.path.join(part_dir, f"part_{part_number}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(content_div))
        
        logger.info(f"Saved HTML content to {html_file}")
        
        # Extract text content
        text_content = content_div.get_text(separator='\n', strip=True)
        
        # Save the text content
        text_file = os.path.join(part_dir, f"part_{part_number}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        logger.info(f"Saved text content to {text_file}")
        
        return {
            "html_file": html_file,
            "text_file": text_file
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping content for Title {title_number}, Part {part_number}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error scraping content for Title {title_number}, Part {part_number}: {e}")
        return None

def scrape_all_titles(max_titles=None):
    """Scrape content for all titles or a subset of titles."""
    # Ensure output directory exists
    ensure_directory_exists(OUTPUT_DIR)
    
    # Get the list of titles
    titles = get_titles()
    
    if not titles:
        logger.error("No titles found. Exiting.")
        return
    
    # Limit the number of titles if specified
    if max_titles:
        titles = titles[:max_titles]
        logger.info(f"Limiting scraping to first {max_titles} titles")
    
    # Create timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Scrape content for each title
    results = {}
    for title in tqdm(titles, desc="Scraping titles"):
        title_number = title.get("number")
        title_name = title.get("name")
        
        logger.info(f"Processing Title {title_number}: {title_name}")
        
        result = scrape_title_content(title_number, title_name)
        if result:
            results[title_number] = {
                "name": title_name,
                "files": result
            }
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(2)
    
    # Save the summary
    summary_file = os.path.join(OUTPUT_DIR, f"scrape_summary_{timestamp}.json")
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "total_titles": len(titles),
            "successful_scrapes": len(results),
            "results": results
        }, f, indent=2)
    
    logger.info(f"Scrape summary saved to: {summary_file}")
    logger.info(f"Successfully scraped {len(results)} out of {len(titles)} titles")
    
    return results

if __name__ == "__main__":
    # By default, scrape all titles
    # Uncomment and modify the line below to limit the number of titles for testing
    # scrape_all_titles(max_titles=3)
    scrape_all_titles()
