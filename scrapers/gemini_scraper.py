# Fichier : scrapers/gemini_scraper.py

from .base_scraper import BaseScraper
from datetime import datetime, timedelta, timezone
import json
import time
import re

class GeminiScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        # Sélecteurs pour la page d'accueil de Gemini
        self.news_section_selector = 'section#news'
        self.article_card_selector = 'div._layout_6eojv_84 > a._card_6eojv_111'
        self.title_selector = 'div._cardTitle_6eojv_143'
        
        # Sélecteurs pour la page d'article sur blog.google
        self.article_content_selectors = ['div.article-body', 'div.rich-text', 'main']
        self.json_ld_selector = 'script[type="application/ld+json"]'

    def _extract_article_content_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=True)
        soup = self._parse_html(html_content)
        
        if not soup:
            return "Contenu non trouvé.", None

        date_str = None
        try:
            json_ld_script = soup.select_one(self.json_ld_selector)
            if json_ld_script and json_ld_script.string:
                data = json.loads(json_ld_script.string)
                date_str = data.get('datePublished')
        except (json.JSONDecodeError, KeyError):
            pass

        content = "Contenu non trouvé."
        for selector in self.article_content_selectors:
            content_container = soup.select_one(selector)
            if content_container:
                # S'il y a un conteneur, extraire tout le texte des paragraphes et des titres
                paragraphs = content_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if paragraphs:
                    content = '\n\n'.join([elem.get_text(strip=True) for elem in paragraphs])
                break # Arrêter après avoir trouvé un sélecteur fonctionnel
        
        return content, date_str

    def scrape(self):
        html_content = self._make_request(url=self.url, use_selenium=True)
        soup = self._parse_html(html_content)
        
        if not soup:
            print("Erreur: Impossible de récupérer ou de parser le contenu HTML.")
            return []
            
        articles = []
        date_limite = datetime.now(timezone.utc) - timedelta(days=7)

        news_section = soup.select_one(self.news_section_selector)
        if not news_section:
            print(f"Section d'actualités non trouvée. Sélecteur utilisé : {self.news_section_selector}")
            return []
            
        article_cards = news_section.select(self.article_card_selector)
        
        if not article_cards:
            print("Aucun article trouvé. Le sélecteur est probablement incorrect.")
            print(f"Sélecteur utilisé : {self.article_card_selector}")
            return []

        for card in article_cards:
            link = card['href'] if card.has_attr('href') else None
            if not link or not link.startswith('http'):
                continue

            title_elem = card.select_one(self.title_selector)
            title = title_elem.get_text(strip=True) if title_elem else "Titre non trouvé."
            
            article_content, post_date_str = self._extract_article_content_from_page(link)
            
            if not post_date_str:
                print(f"Avertissement: Date non trouvée pour l'article '{title}'. Article ignoré.")
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
                    'content': article_content
                })
        
        return articles