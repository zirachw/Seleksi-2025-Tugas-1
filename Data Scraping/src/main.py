import os
import sys
import logging

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

scraper = SpotifyScraper(START_URL, CHROMEDRIVER_PATH, CHROME_PATH)
scraper.run()

if scraper:
    scraper.close_browser()
