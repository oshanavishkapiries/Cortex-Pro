"""
Simple Web Video Link Extractor

Purpose:
    This script loads a given website URL and extracts all video links ending with .m3u8 or .mp4.
    It scans the HTML content for 'src' and 'href' attributes, as well as general regex matching
    for direct video URLs embedded in scripts or plain text.

Usage:
    python simple_web_videoo_link_extractor.py --url "https://streamimdb.ru/embed/movie/tt0848228"

Flags/Arguments:
    -u, --url       (Required) The URL of the website to scrape for video links.
    -t, --timeout   (Optional) Timeout in seconds for the HTTP request (default: 10).
    -v, --verbose   (Optional) Enable verbose logging.

Installation & Setup:
    1. Create a virtual environment:
       python -m venv venv
       source venv/bin/activate  # On Windows use: venv\Scripts\activate

    2. Install the required packages:
       pip install requests beautifulsoup4

"""

import argparse
import logging
import re
import sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURATION
# ==========================================
DEFAULT_TIMEOUT = 10
# Supported video extensions
TARGET_EXTENSIONS = ['.m3u8', '.mp4']
# User-Agent header to mimic a standard web browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# ==========================================
# LOGIC IMPLEMENTATION
# ==========================================

def setup_logger(verbose: bool) -> logging.Logger:
    """Configures the logger based on the verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)

def extract_video_links(url: str, timeout: int, logger: logging.Logger) -> list:
    """
    Fetches the website content and extracts video links.
    """
    headers = {"User-Agent": USER_AGENT}
    logger.debug(f"Sending GET request to {url} with timeout {timeout}s.")
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        # Save the raw response content to a file
        with open("response_content.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        logger.debug("Saved response content to response_content.html")

        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch the URL. Error: {e}")
        return []

    logger.debug("Successfully fetched the web page. Parsing content...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    extracted_links = set()

    # Approach 1: Check standard tags and attributes (e.g., src, href)
    for tag in soup.find_all(True):
        if tag.has_attr('src'):
            link = tag['src']
            if any(link.endswith(ext) for ext in TARGET_EXTENSIONS):
                extracted_links.add(urljoin(url, link))
        if tag.has_attr('href'):
            link = tag['href']
            if any(link.endswith(ext) for ext in TARGET_EXTENSIONS):
                extracted_links.add(urljoin(url, link))

    # Approach 2: Regex search across the entire raw HTML
    # Matches URLs ending in .m3u8 or .mp4
    regex_pattern = r'(https?://[^\s\'"]+?(?:\.m3u8|\.mp4))'
    matches = re.findall(regex_pattern, response.text)
    for match in matches:
        extracted_links.add(match)

    return list(extracted_links)

def main():
    parser = argparse.ArgumentParser(description="Extract .m3u8 and .mp4 video links from a given URL.")
    parser.add_argument("-u", "--url", required=True, help="The URL of the website to scrape.")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds for the HTTP request.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    
    args = parser.parse_args()
    logger = setup_logger(args.verbose)

    logger.info(f"Starting video link extraction for: {args.url}")
    
    links = extract_video_links(args.url, args.timeout, logger)
    
    if not links:
        logger.info("No target video links (.m3u8, .mp4) found on the page.")
        sys.exit(0)

    logger.info(f"Found {len(links)} video link(s):")
    for link in links:
        print(f" -> {link}")

if __name__ == "__main__":
    main()
