import logging
import os
import sys
from typing import List, Dict
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service

sys.path.append(os.path.join(os.path.dirname(__file__)))
from extractor.genre import GenreExtractor
from extractor.collection import CollectionExtractor

CHROMEDRIVER_PATH = 'D:/Exe/chromedriver-win64/chromedriver.exe'
CHROME_PATH = 'D:/Exe/chrome-win64/chrome.exe'
START_URL = "https://open.spotify.com/search"

class SpotifyScraper:
    """Main scraper class for extracting Spotify data
    
    Attributes:
        start_url: Initial Spotify search URL
        genre_links: List of extracted genre data
        collections: List of extracted collection data
        browser: Selenium WebDriver instance
    """
    
    def __init__(self, start_url: str, chromedriver_path: str, chrome_path: str) -> None:
        """Initialize the SpotifyScraper with browser configuration
        
        Args:
            start_url: Initial Spotify search URL to begin scraping
            chromedriver_path: File path to ChromeDriver executable
            chrome_path: File path to Chrome browser executable
            
        Raises:
            WebDriverException: If browser initialization fails
        """

        self.start_url = start_url
        self.genre_links: List[Dict[str, str]] = []
        self.collections: List[Dict[str, str]] = []
        
        self.browser = self._initialize_browser(chromedriver_path, chrome_path)
        self.genre_extractor = GenreExtractor(self.browser)
        self.collection_extractor = CollectionExtractor(self.browser)
        
        self.browser.get(self.start_url)
        logging.info(f"[Main] Navigated to {self.start_url}")
    
    def _initialize_browser(self, chromedriver_path: str, chrome_path: str) -> webdriver.Chrome:
        """
        Args:
            chromedriver_path: File path to ChromeDriver executable
            chrome_path: File path to Chrome browser executable
            
        Returns:
            Configured Chrome WebDriver instance
            
        Raises:
            WebDriverException: If browser initialization fails
        """

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.binary_location = chrome_path
        
        try:
            browser = webdriver.Chrome(
                service=Service(chromedriver_path),
                options=chrome_options
            )
            browser.set_page_load_timeout(30)
            logging.info("[Main] Browser initialized successfully")
            return browser
        
        except WebDriverException as e:
            logging.error(f"[Main] Failed to initialize browser: {str(e)}")
            raise

    def _process_genre(self) -> None:
        """Extract and save genre data

        Raises:
            WebDriverException: If browser automation fails
            Exception: If any step in the genre extraction process fails
        """

        try:
            self.genre_links = self.genre_extractor.get_data()
        except Exception as e:
            logging.error(f"[Genre] {str(e)}")
            raise
        
        if not self.genre_links:
            logging.info("[Genre] No genre links found!")
            return
        
        print(f"\n[Main] Found {len(self.genre_links)} genres:")

        for genre in self.genre_links[:10]:
            print(f"- {genre['name']}: {genre['url']}")
        if len(self.genre_links) > 10:
            print(f"... and {len(self.genre_links) - 10} more\n")
        
        try:
            self.genre_extractor.save_to_json("Data Scraping/data/genre.json")
        except Exception as e:
            logging.error(f"[Genre] Error saving genres: {str(e)}")
            raise

    def _process_collection(self) -> None:
        """Extract and save collection data from genres
        
        Raises:
            WebDriverException: If browser automation fails
            Exception: If any step in the collection extraction process fails
        """

        if not self.genre_links:
            logging.warning("[Collection] No genre links available for collection extraction")
            return
        
        try:
            self.collections = self.collection_extractor.get_data(self.genre_links)
        except Exception as e:
            logging.error(f"[Collection] {str(e)}")
            raise
        
        if not self.collections:
            print("No collections found!")
            return
        
        print(f"\n[Main] Total collections found: {len(self.collections)}")
        
        genre_collection_count = {}
        for collection in self.collections:
            genre_id = collection['genre_id']
            genre_collection_count[genre_id] = genre_collection_count.get(genre_id, 0) + 1
        
        print("\nCollections per genre:")
        for i, genre in enumerate(self.genre_links[:10]):
            count = genre_collection_count.get(genre['genre_id'], 0)
            print(f"- {genre['name']}: {count} collections")
        
        if len(self.genre_links) > 10:
            remaining_count = sum(genre_collection_count.get(g['genre_id'], 0) for g in self.genre_links[10:])
            print(f"- ... and {remaining_count} more collections from other genres")
        
        print(f"\n[Main] Sample collections:")
        for collection in self.collections[:5]:
            genre_name = next((g['name'] for g in self.genre_links if g['genre_id'] == collection['genre_id']), 'Unknown')
            print(f"- {collection['name']} (from {genre_name})")
        
        if len(self.collections) > 5:
            print(f"... and {len(self.collections) - 5} more\n")
        
        try:
            self.collection_extractor.save_to_json("Data Scraping/data/collections.json")
        except Exception as e:
            logging.error(f"[Collection] Error saving collections: {str(e)}")
            raise
        
    def run(self) -> None:
        """Run the complete scraping process
        
        Orchestrates the full Spotify data extraction workflow
        
        Raises:
            WebDriverException: If browser automation fails
            Exception: If any step in the scraping process fails
        """

        try:
            logging.info("[Main] Starting genre extraction...")
            self._process_genre()
            logging.info("[Main] Genre extraction completed successfully")

            logging.info("[Main] Starting collection extraction...")
            self._process_collection()
            logging.info("[Main] Collection extraction completed successfully")

        except WebDriverException as e:
            logging.error(f"[Main - WebDriverException] {str(e)}")

        except Exception as e:
            logging.error(f"[Main - Exception] {str(e)}")

    def close_browser(self) -> None:
        """Safely terminates the Chrome WebDriver session."""

        if hasattr(self, 'browser') and self.browser:
            self.browser.quit()
            logging.info("[Main] Browser closed")
