import os
import json
import logging
from typing import List, Dict, Any
from selenium import webdriver
from abc import ABC, abstractmethod

class Extractor(ABC):
    """Abstract base class for Spotify data extractors
    
    Defines the common interface and functionality
    for all Spotify data extraction components.
    
    Attributes:
        browser: Selenium WebDriver instance for web automation
        data: List of extracted data dictionaries
    """
    
    def __init__(self, browser: webdriver.Chrome) -> None:
        """Initialize the Extractor with a browser instance
        
        Args:
            browser: Selenium Chrome WebDriver instance
        """
        self.browser = browser
        self.data: List[Dict[str, Any]] = []
    
    @abstractmethod
    def get_data(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Abstract method to extract data from Spotify
        
        This method must be implemented by subclasses to define
        their specific data extraction logic.
        
        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments
            
        Returns:
            List of dictionaries containing extracted data
        """
        pass
    
    def save_to_json(self, filename: str) -> None:
        """Save extracted data to JSON file with UTF-8 encoding
        
        Args:
            filename: Path to the output JSON file
            
        Raises:
            OSError: If file cannot be created or written
        """
        
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logging.info(f"[Extractor] Created directory: {directory}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        logging.info(f"[Extractor] Data saved to {filename}")
