# Fichier : scrapers/base_scraper.py

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class BaseScraper(ABC):
    """
    Classe de base pour tous les web scrapers.
    Elle gère les requêtes HTTP, le parsing HTML et l'utilisation de Selenium si nécessaire.
    """
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _make_request(self, url=None, use_selenium=False):
        if url is None:
            url = self.url
        import os
        if use_selenium:
            print("Utilisation de Selenium...")
            options = webdriver.ChromeOptions()
            # Options recommandées pour éviter les erreurs
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            # Permet de désactiver le mode headless pour debug via une variable d'env
            if os.getenv('SELENIUM_HEADLESS', '1') == '1':
                options.add_argument('--headless=new')
            # Utilise un User-Agent pour paraître plus crédible
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                driver.set_page_load_timeout(180)
                driver.get(url)
                import time
                time.sleep(8)  # Laisse le JS charger sur tous les sites
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                page_source = driver.page_source
            except Exception as e:
                print(f"Erreur Selenium lors de la requête sur {url}: {e}")
                print("Le problème pourrait être lié à la version de Chrome/ChromeDriver ou aux options du navigateur.")
                print("Assurez-vous que Chrome est à jour ou essayez de désactiver le mode headless pour le débogage (export SELENIUM_HEADLESS=0).")
                return None
            finally:
                try:
                    driver.quit()
                except Exception:
                    pass
            return page_source
        else:
            # ... (le code pour requests reste inchangé) ...
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Erreur requests lors de la requête sur {url}: {e}")
                return None

    def _parse_html(self, html_content):
        """
        Parse le contenu HTML brut en un objet BeautifulSoup.
        """
        if html_content:
            return BeautifulSoup(html_content, 'html.parser')
        return None
    
    @abstractmethod
    def scrape(self):
        """
        Méthode abstraite à implémenter dans les sous-classes pour le scraping.
        """
        pass