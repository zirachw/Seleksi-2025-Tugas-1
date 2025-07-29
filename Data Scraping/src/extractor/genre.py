import os
import sys
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__)))
from extractor.extractor import Extractor

START_URL = "https://open.spotify.com/search"

class GenreExtractor(Extractor):
    """Genre data extractor from links in Spotify search page
    
    Inherits from Extractor abstract base class.
    
    Attributes:
        genre_links: List of extracted genre data dictionaries
    """
    
    def __init__(self, browser) -> None:
        """Initialize the GenreExtractor with a browser instance
        
        Args:
            browser: Selenium Chrome WebDriver instance
        """
        super().__init__(browser)
        self.genre_links: List[Dict[str, str]] = []
    
    def get_data(self, start_url: str = START_URL) -> List[Dict[str, str]]:
        """Extract all genre data
        
        Args:
            start_url: The Spotify search page URL to scrape from
            
        Returns:
            List of dictionaries containing genre data with keys:
            - name: Genre display name
            - url: Full Spotify genre URL
            - genre_id: Unique genre identifier
            
        Raises:
            TimeoutException: If page fails to load within timeout
            WebDriverException: If browser automation fails
        """
        
        page_source = self.browser.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        genre_links = soup.find_all('a', {
            'class': 'CqCtb3wr4SK8AiZwxeH0',
            'draggable': 'false'
        })
        
        # Fallback selector
        if not genre_links:
            genre_links = soup.find_all('a', href=lambda x: isinstance(x, str) and '/genre/' in x)
        
        extracted_links = []
        for link in genre_links:
            genre_data = self._process_genre_link(link)
            if genre_data:
                extracted_links.append(genre_data)
                logging.info(f"[Genre] Found genre: {genre_data['name']}")
        
        self.genre_links = extracted_links
        self.data = extracted_links
        logging.info(f"[Genre] Successfully extracted {len(extracted_links)} genre links")

        return extracted_links
            
    def _process_genre_link(self, link: Any) -> Optional[Dict[str, str]]:
        """Process a single genre link and extract data
        
        Args:
            link: BeautifulSoup element representing a genre link
            
        Returns:
            Dictionary with genre data or None if extraction fails:
            - name: Genre display name from title attribute  
            - url: Full normalized Spotify URL
            - genre_id: Extracted genre identifier
        """
        
        href = link.get('href')
        if not href or not href.startswith('/genre/'):
            return None
        
        span = link.find('span', class_=lambda x: x and 'e-91000-text' in str(x))
        genre_name = span.get('title') if span else 'Unknown'

        if 'Podcast' in genre_name:
            return None
        
        # Genres with no collection
        if genre_name in ['Made For You', 'Discover', 'Karaoke', 'Blues', 
                          'Travel', 'Funk & Disco', 'Carribean']:
            return None
        
        full_url = f"https://open.spotify.com{href}"
        genre_id = href.split('/')[-1]
        
        return {
            'genre_id': genre_id,
            'name': genre_name,
            'url': full_url
        }
