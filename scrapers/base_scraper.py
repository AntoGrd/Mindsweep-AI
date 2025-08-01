# Fichier : scrapers/base_scraper.py

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup

class BaseScraper(ABC): # La classe est "abstraite"
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': '...'} # Un bon User-Agent

    def _make_request(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête sur {self.url}: {e}")
            return None

    def _parse_html(self, html_content):
        if html_content:
            return BeautifulSoup(html_content, 'html.parser')
        return None
    
    @abstractmethod
    def scrape(self): # Cette méthode doit être implémentée par les sous-classes
        pass


