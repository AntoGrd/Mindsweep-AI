# Fichier : scrapers/openai_scraper.py

from .base_scraper import BaseScraper
from datetime import datetime, timedelta, timezone
import time
import re

class OpenAIScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        # Sélecteurs pour la page d'accueil d'OpenAI
        self.article_card_selector = 'a[href^="/index/"]' 
        self.title_selector = 'div.mb-2xs.text-h5'
        self.date_selector = 'time'
        
        # Sélecteurs pour le contenu d'un article individuel
        self.article_content_selector = 'main'
        self.article_date_selector = 'time'

    def _extract_article_content_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=True)
        soup = self._parse_html(html_content)
        if soup:
            date_elem = soup.select_one(self.article_date_selector)
            date_str = date_elem['datetime'] if date_elem and 'datetime' in date_elem.attrs else None
            
            content_elem = soup.select_one(self.article_content_selector)
            content = content_elem.get_text(separator='\n', strip=True) if content_elem else "Contenu non trouvé."
            
            return content, date_str
        return "Contenu non trouvé.", None

    def _extract_article_title_content_date_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=True)
        soup = self._parse_html(html_content)
        if soup:
            # Titre
            title_elem = soup.find(['h1', 'h2'])
            title = title_elem.get_text(strip=True) if title_elem else "Titre non trouvé."
            # Date
            date_elem = soup.select_one(self.article_date_selector)
            date_str = date_elem['datetime'] if date_elem and 'datetime' in date_elem.attrs else None
            # Contenu
            content_elem = soup.select_one(self.article_content_selector)
            content = content_elem.get_text(separator='\n', strip=True) if content_elem else "Contenu non trouvé."
            return title, content, date_str
        return "Titre non trouvé.", "Contenu non trouvé.", None

    def scrape(self):
        html_content = self._make_request(url=self.url, use_selenium=True)
        soup = self._parse_html(html_content)
        
        if not soup:
            print("Erreur: Impossible de récupérer ou de parser le contenu HTML.")
            return []
            
        articles = []
        date_limite = datetime.now(timezone.utc) - timedelta(days=7)

        article_cards = soup.select(self.article_card_selector)
        
        if not article_cards:
            print("Aucun article trouvé. Le sélecteur est probablement incorrect.")
            print(f"Sélecteur utilisé : {self.article_card_selector}")
            return []

        seen_links = set()
        
        for card in article_cards:
            link = f"https://openai.com{card['href']}" if card.has_attr('href') else None
            if not link or link in seen_links:
                continue
            seen_links.add(link)

            title, content, post_date_str = self._extract_article_title_content_date_from_page(link)
            
            if not post_date_str or title == "Titre non trouvé." or content == "Contenu non trouvé.":
                print(f"Avertissement: Titre, contenu ou date non trouvés pour l'article {link}. Article ignoré.")
                continue

            try:
                article_date = datetime.fromisoformat(post_date_str)
                if article_date.tzinfo is None:
                    article_date = article_date.replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"Avertissement : Impossible de parser la date '{post_date_str}'. Article ignoré.")
                continue

            if article_date >= date_limite:
                articles.append({
                    'title': title,
                    'link': link,
                    'date': post_date_str,
                    'content': content
                })
            else:
                print(f"Article '{title}' a plus de 7 jours. Fin du scraping d'OpenAI.")
                break
        return articles