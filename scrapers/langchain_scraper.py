# Fichier : scrapers/langchain_scraper.py

from .base_scraper import BaseScraper
from datetime import datetime, timedelta, timezone
import time
import re

class LangChainScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        # Sélecteurs pour la page d'accueil de LangChain
        self.article_card_selector = 'article.post-card'
        self.title_link_selector = 'a.post-card__content-link'
        self.title_selector = 'h2.post-card__title'
        self.date_selector = 'time'
        
        # Sélecteurs pour la page d'article
        self.article_title_selector = 'h1.article-header__title'
        self.article_content_selector = 'div.article-content'
        self.article_date_selector = 'time.article-header__meta--date'
        
    def _extract_article_content_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=False)
        soup = self._parse_html(html_content)
        if soup:
            # Titre
            title_elem = soup.select_one(self.article_title_selector)
            title = title_elem.get_text(strip=True) if title_elem else "Titre non trouvé."
            # Contenu principal
            content_elem = soup.select_one(self.article_content_selector)
            content = ""
            if content_elem:
                for element in content_elem.find_all(['h1','h2','h3','h4','h5','h6','p','ul','ol','pre']):
                    text = element.get_text(strip=True)
                    if text:
                        content += text + "\n\n"
            if not content:
                content = "Contenu non trouvé."
            # Date
            date_elem = soup.select_one(self.article_date_selector)
            date_str = date_elem['datetime'] if date_elem and date_elem.has_attr('datetime') else None
            return content, date_str
        return "Contenu non trouvé.", None

    def scrape(self):
        html_content = self._make_request(url=self.url, use_selenium=False)
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

        for card in article_cards:
            link_elem = card.select_one(self.title_link_selector)
            link = link_elem['href'] if link_elem and link_elem.has_attr('href') else None
            if not link:
                continue
            
            if not link.startswith('http'):
                link = f"https://blog.langchain.com{link}"

            # On ne récupère le titre et la date que depuis la page d'article (plus fiable)
            article_title, article_content, post_date_str = self._extract_article_title_content_date_from_page(link)

            try:
                article_date = datetime.fromisoformat(post_date_str)
                if article_date.tzinfo is None:
                    article_date = article_date.replace(tzinfo=timezone.utc)
            except Exception:
                print(f"Avertissement : Impossible de parser la date '{post_date_str}'. Article ignoré.")
                continue

            if article_date >= date_limite:
                articles.append({
                    'title': article_title,
                    'link': link,
                    'date': post_date_str,
                    'content': article_content
                })
            else:
                print(f"Article à plus de 7 jours. Fin du scraping de LangChain.")
                break
        return articles

    def _extract_article_title_content_date_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=False)
        soup = self._parse_html(html_content)
        if soup:
            # Titre
            title_elem = soup.select_one(self.article_title_selector)
            title = title_elem.get_text(strip=True) if title_elem else "Titre non trouvé."
            # Contenu principal
            content_elem = soup.select_one(self.article_content_selector)
            content = ""
            if content_elem:
                for element in content_elem.find_all(['h1','h2','h3','h4','h5','h6','p','ul','ol','pre']):
                    text = element.get_text(strip=True)
                    if text:
                        content += text + "\n\n"
            if not content:
                content = "Contenu non trouvé."
            # Date
            date_elem = soup.select_one(self.article_date_selector)
            date_str = date_elem['datetime'] if date_elem and date_elem.has_attr('datetime') else None
            return title, content, date_str
        return "Titre non trouvé.", "Contenu non trouvé.", None