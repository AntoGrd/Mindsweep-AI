from .base_scraper import BaseScraper
from datetime import datetime, timezone, timedelta
import time

class OllamaScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.article_card_selector = 'a.group.border-b.py-10'
        self.article_title_selector = 'h2.text-xl'
        self.article_date_selector = 'h3.text-sm.text-neutral-500'
        self.article_content_selector = 'div.prose'

    def _extract_article_content_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=False)
        soup = self._parse_html(html_content)
        if soup:
            content_elem = soup.select_one('section.prose')
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

    def _parse_date(self, date_str, date_elem=None):
        # Essaye le format '2025-08-05 00:00:00 +0000 UTC'
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z %Z")
        except Exception:
            pass
        # Essaye le format texte anglais 'August 5, 2025'
        if date_elem:
            try:
                return datetime.strptime(date_elem.get_text(strip=True), "%B %d, %Y").replace(tzinfo=timezone.utc)
            except Exception:
                pass
        # Essaye le format ISO
        try:
            return datetime.fromisoformat(date_str)
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
            print("Aucun article trouvé sur la page Ollama Blog.")
            return []
        for card in article_cards:
            title_elem = card.select_one(self.article_title_selector)
            title = title_elem.get_text(strip=True) if title_elem else "Titre non trouvé."
            date_elem = card.select_one(self.article_date_selector)
            date_str = date_elem['datetime'] if date_elem and date_elem.has_attr('datetime') else None
            article_date = self._parse_date(date_str, date_elem)
            if not article_date:
                print(f"Avertissement : Impossible de parser la date '{date_str}'. Article ignoré.")
                continue
            if article_date.tzinfo is None:
                article_date = article_date.replace(tzinfo=timezone.utc)
            if article_date >= date_limite:
                link = card['href'] if card.has_attr('href') else None
                if link and not link.startswith('http'):
                    link = f"https://ollama.com{link}"
                content = self._extract_article_content_from_page(link) if link else "Contenu non trouvé."
                articles.append({
                    'title': title,
                    'link': link,
                    'date': article_date.isoformat(),
                    'content': content
                })
            else:
                print(f"Article '{title}' a plus de 7 jours. Fin du scraping de Ollama.")
                break
        return articles
