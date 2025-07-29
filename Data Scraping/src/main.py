import os
import sys
import logging
import urllib3

sys.path.append(os.path.join(os.path.dirname(__file__)))
from scraper import SpotifyScraper

CHROMEDRIVER_PATH = 'D:/Exe/chromedriver-win64/chromedriver.exe'
CHROME_PATH = 'D:/Exe/chrome-win64/chrome.exe'
START_URL = "https://open.spotify.com/search"

"""
Main Program Execution
"""

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.ERROR)

scraper = None

try:
    scraper = SpotifyScraper(START_URL, CHROMEDRIVER_PATH, CHROME_PATH)
    scraper.run()
except KeyboardInterrupt:
    logging.info("[Main] KeyboardInterrupt received, shutting down...")
finally:
    if scraper:
        scraper.close_browser()
