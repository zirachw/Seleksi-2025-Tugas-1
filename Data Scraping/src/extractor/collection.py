import os
import sys
import logging
import time

from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.join(os.path.dirname(__file__)))
from extractor.extractor import Extractor

class CollectionExtractor(Extractor):
    """Collection data extractor from links in genre pages
    
    Inherits from Extractor abstract base class.
    
    Attributes:
        collections: List of extracted collection data dictionaries
    """
    
    def __init__(self, browser) -> None:
        """Initialize the CollectionExtractor with a browser instance
        
        Args:
            browser: Selenium Chrome WebDriver instance
        """
        super().__init__(browser)
        self.collections: List[Dict[str, str]] = []
    
    def get_data(self, genre_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Extract collections from multiple genres
        
        Args:
            genre_list: List of genre dictionaries with 'url', 'genre_id', and 'name' keys
            
        Returns:
            List of dictionaries containing collection data with keys:
            - name: Collection display name
            - url: Full Spotify collection URL
            - collection_id: Unique collection identifier
            - genre_id: Associated genre identifier
            
        Raises:
            TimeoutException: If any genre page fails to load
            WebDriverException: If browser automation fails
        """

        all_collections = []
        
        for genre in genre_list:
            genre_url = genre['url']
            genre_id = genre['genre_id']
            genre_name = genre['name']
            
            logging.info(f"[Collection] Processing collections for genre: {genre_name}")
            collections = self._get_collections_from_genre(genre_url, genre_id)
            all_collections.extend(collections)
            
            time.sleep(2)
        
        self.collections = all_collections
        self.data = all_collections  # Store in parent class data attribute
        logging.info(f"[Collection] Total collections extracted: {len(all_collections)}")

        return all_collections
    
    def _get_collections_from_genre(self, genre_url: str, genre_id: str) -> List[Dict[str, str]]:
        """Extract collections from a single genre page
        
        Args:
            genre_url: Full URL of the genre page to scrape
            genre_id: Unique identifier for the genre
            
        Returns:
            List of dictionaries containing collection data:
            - name: Collection display name
            - url: Full normalized Spotify URL
            - collection_id: Extracted collection identifier
            - genre_id: Associated genre identifier
            
        Raises:
            TimeoutException: If page fails to load within timeout
            WebDriverException: If browser automation fails
        """

        logging.info(f"[Collection] Navigating to genre page: {genre_url}")
        self.browser.get(genre_url)
        
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        time.sleep(3)
        
        page_source = self.browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        see_all_links = soup.find_all('a', {
            'data-testid': 'see-all-link',
            'tabindex': '-1'
        })
        
        # Fallback selector
        if not see_all_links:
            see_all_links = soup.find_all('a', href=lambda x: isinstance(x, str) and '/genre/section' in x)
        
        extracted_collections = []
        for link in see_all_links:
            collection_data = self._process_collection_link(link, genre_id)
            if collection_data:
                extracted_collections.append(collection_data)
                logging.info(f"[Collection] Found collection: {collection_data['name']}")
        
        logging.info(f"[Collection] Successfully extracted {len(extracted_collections)} collections from genre")

        return extracted_collections
    
    def _process_collection_link(self, link: Any, genre_id: str) -> Optional[Dict[str, str]]:
        """Process a single collection link and extract data

        Args:
            link: BeautifulSoup element representing a collection link
            genre_id: Associated genre identifier for relationship mapping
            
        Returns:
            Dictionary with collection data or None if extraction fails:
            - collection_id: Extracted collection identifier
            - genre_id: Associated genre identifier
            - name: Collection display name from link text
            - url: Full normalized Spotify URL
        """

        href = link.get('href')
        if not href:
            return None
        
        collection_name = link.get_text(strip=True)
        if not collection_name:
            return None
        
        full_url = f"https://open.spotify.com{href}" if href.startswith('/') else href
        collection_id = href.split('/')[-1]
        
        return {
            'collection_id': collection_id,
            'genre_id': genre_id,
            'name': collection_name,
            'url': full_url
        }
