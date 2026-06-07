"""
Puppeteer Web Video Link Extractor

Purpose:
    This script uses Pyppeteer (the Python port of Puppeteer) along with stealth plugins
    to bypass bot detection and load a given website. Once loaded, it extracts all video 
    links ending with .m3u8 or .mp4. It intercepts network requests to catch dynamically 
    loaded video streams and parses the final rendered HTML content.

Usage:
    python puppeteer_web_video_link_extractor.py --url "https://streamimdb.ru/embed/movie/tt0848228"

Flags/Arguments:
    -u, --url       (Required) The URL of the website to scrape for video links.
    -t, --timeout   (Optional) Timeout in seconds for page load (default: 30).
    -v, --verbose   (Optional) Enable verbose logging.

Installation & Setup:
    1. Create a virtual environment:
       python -m venv venv
       source venv/bin/activate  # On Windows use: venv/Scripts/activate

    2. Install the required packages:
       pip install pyppeteer pyppeteer_stealth beautifulsoup4

    3. Note: On the first run, Pyppeteer will automatically download a compatible Chromium binary.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pyppeteer import launch
from pyppeteer.errors import PyppeteerError
from pyppeteer_stealth import stealth

# ==========================================
# CONFIGURATION
# ==========================================
DEFAULT_TIMEOUT = 200
# Supported video extensions
TARGET_EXTENSIONS = ['.m3u8', '.mp4']
# Headless mode for browser
HEADLESS_MODE = True

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

async def extract_video_links(url: str, timeout: int, logger: logging.Logger, debug_json: bool) -> list:
    """
    Launches a stealth Pyppeteer browser, loads the page, intercepts network requests,
    and parses the DOM to extract video links.
    """
    logger.debug("Launching browser with stealth settings...")
    try:
        browser = await launch(
            headless=HEADLESS_MODE,
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--window-size=1920,1080'
            ],
            ignoreDefaultArgs=['--enable-automation']
        )
        page = await browser.newPage()
        # Set a realistic user agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        # Apply pyppeteer_stealth
        await stealth(page)
    except PyppeteerError as e:
        logger.error(f"Failed to launch browser: {e}")
        return []

    extracted_links = set()
    debug_data = {"url": url, "requests": [], "html_content": ""}
    screenshot_task = None

    if debug_json:
        if os.path.exists("debug_requests.json"):
            os.remove("debug_requests.json")
        if os.path.exists("debug_screenshots"):
            shutil.rmtree("debug_screenshots")
        os.makedirs("debug_screenshots", exist_ok=True)

        async def screenshot_loop():
            for i in range(5):
                await asyncio.sleep(2)
                try:
                    await page.screenshot({'path': f'debug_screenshots/screenshot_{i}.png', 'fullPage': True})
                except Exception as e:
                    logger.debug(f"Screenshot error: {e}")
        
        screenshot_task = asyncio.create_task(screenshot_loop())

    # Intercept network requests to catch dynamically loaded media streams
    await page.setRequestInterception(True)

    async def intercept_request(request):
        req_url = request.url
        if debug_json:
            debug_data["requests"].append({
                "url": req_url,
                "method": request.method,
                "resourceType": request.resourceType
            })
        if any(req_url.endswith(ext) for ext in TARGET_EXTENSIONS):
            logger.debug(f"Intercepted media request: {req_url}")
            extracted_links.add(req_url)
        # Handle navigation requests to avoid pyppeteer breaking in some scenarios
        try:
            await request.continue_()
        except PyppeteerError:
            pass

    page.on('request', lambda req: asyncio.ensure_future(intercept_request(req)))

    logger.info(f"Navigating to {url} (Timeout: {timeout}s)...")
    try:
        # Timeout is in milliseconds for pyppeteer
        await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': timeout * 1000})
    except PyppeteerError as e:
        logger.warning(f"Page navigation encountered an issue or timed out: {e}")
        # Proceed anyway as the page might have partially loaded

    logger.debug("Parsing rendered HTML content...")
    try:
        content = await page.content()
    except PyppeteerError as e:
        logger.error(f"Failed to retrieve page content: {e}")
        await browser.close()
        return list(extracted_links)

    if debug_json:
        if screenshot_task:
            await screenshot_task
        debug_data["html_content"] = content
        with open("debug_requests.json", "w", encoding="utf-8") as f:
            json.dump(debug_data, f, indent=4, ensure_ascii=False)
        logger.info("Debug JSON saved to debug_requests.json and screenshots saved to debug_screenshots/")

    await browser.close()
    logger.debug("Browser closed.")

    soup = BeautifulSoup(content, 'html.parser')

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
    regex_pattern = r'(https?://[^\s\'"]+?(?:\.m3u8|\.mp4))'
    matches = re.findall(regex_pattern, content)
    for match in matches:
        extracted_links.add(match)

    return list(extracted_links)

def main():
    parser = argparse.ArgumentParser(description="Extract .m3u8 and .mp4 video links using stealth Pyppeteer.")
    parser.add_argument("-u", "--url", required=True, help="The URL of the website to scrape.")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds for the page load.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--debug", dest="debug_json", action="store_true", help="Clean old debug files, dump requests to JSON, and save a chain of screenshots.")
    
    args = parser.parse_args()
    logger = setup_logger(args.verbose)

    logger.info(f"Starting Puppeteer-based video link extraction for: {args.url}")
    
    # Run the asynchronous extraction
    links = asyncio.run(extract_video_links(args.url, args.timeout, logger, args.debug_json))
    
    if not links:
        logger.info("No target video links (.m3u8, .mp4) found on the page or intercepted during load.")
        sys.exit(0)

    logger.info(f"Found {len(links)} video link(s):")
    for link in links:
        print(f" -> {link}")

if __name__ == "__main__":
    main()
