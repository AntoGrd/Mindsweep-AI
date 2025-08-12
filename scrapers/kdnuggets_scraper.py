from .base_scraper import BaseScraper
from datetime import datetime, timezone, timedelta
import time
import re

class KDNuggetsScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.article_card_selector = 'li.li-has-thumb'
        self.title_selector = 'div.li-has-thumb__content > a'
        self.date_selector = 'div.author-link'
        self.article_content_selector = 'div.post'  # Correction ici

    def _extract_article_content_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=False)
        soup = self._parse_html(html_content)
        if soup:
            content_elem = soup.select_one(self.article_content_selector)
            content = ""
            if content_elem:
                for element in content_elem.find_all(['h1','h2','h3','h4','h5','h6','p','ul','ol','pre','img']):
                    if element.name == 'img' and element.has_attr('src'):
                        alt = element.get('alt', '')
                        content += f"[Image: {alt}] {element['src']}\n\n"
                    else:
                        text = element.get_text(strip=True)
                        if text:
                            content += text + "\n\n"
            if not content:
                content = "Contenu non trouvé."
            return content
        return "Contenu non trouvé."

    def _parse_date_from_author_link(self, author_link_text):
        # Ex: 'By <strong>...</strong> ... on August 8, 2025 in ...'
        match = re.search(r'on ([A-Za-z]+ \d{1,2}, \d{4})', author_link_text)
        if match:
            try:
                article_date = datetime.strptime(match.group(1), "%B %d, %Y").replace(tzinfo=timezone.utc)
                return article_date
            except Exception:
                pass
        return None

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
            print("Aucun article trouvé sur la page KDNuggets.")
            return []
        for card in article_cards:
            title_elem = card.select_one(self.title_selector)
            title = title_elem.get_text(strip=True) if title_elem else "Titre non trouvé."
            link = title_elem['href'] if title_elem and title_elem.has_attr('href') else None
            date_elem = card.select_one(self.date_selector)
            date_str = None
            article_date = None
            if date_elem:
                date_text = date_elem.get_text(" ", strip=True)
                article_date = self._parse_date_from_author_link(date_text)
                if article_date:
                    date_str = article_date.isoformat()
            if not article_date:
                print(f"Avertissement : Impossible de parser la date pour l'article '{title}'. Article ignoré.")
                continue
            if article_date >= date_limite:
                content = self._extract_article_content_from_page(link) if link else "Contenu non trouvé."
                articles.append({
                    'title': title,
                    'link': link,
                    'date': date_str,
                    'content': content
                })
            else:
                print(f"Article '{title}' a plus de 7 jours. Fin du scraping de KDNuggets.")
                break
        return articles
