import logging
from typing import List, Dict
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service

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

    def close_browser(self) -> None:
        """Safely terminates the Chrome WebDriver session."""

        if hasattr(self, 'browser') and self.browser:
            self.browser.quit()
