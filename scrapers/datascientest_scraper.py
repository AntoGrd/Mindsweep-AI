from .base_scraper import BaseScraper
from datetime import datetime, timezone, timedelta
import time
import re

class DatascientestScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.article_selector = 'h3 > a, h2 > a, h4 > a'  # Les titres d'articles sont souvent dans h3/h2/h4 > a
        self.date_pattern = re.compile(r'• (\w+ \d{1,2}, \d{4})')
        self.max_days = 7

    def _extract_article_content(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url, use_selenium=False)
        soup = self._parse_html(html_content)
        # Suppression du debug HTML
        if not soup:
            return "Contenu non trouvé."
        # Nouvelle méthode : cibler le contenu principal typique WordPress/Elementor
        main_content = soup.find("div", class_="elementor-widget-theme-post-content")
        if not main_content:
            main_content = soup.find("article")
        if not main_content:
            sections = soup.find_all("section")
            main_content = max(sections, key=lambda s: len(s.get_text()), default=None) if sections else None
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
            return text if text else "Contenu non trouvé."
        return "Contenu non trouvé."

    def scrape(self):
        articles = []
        url = self.url
        date_limite = datetime.now(timezone.utc) - timedelta(days=self.max_days)
        page = 1
        seen_links = set()  # To avoid duplicates
        while True:
            page_url = url if page == 1 else f"{url}/page/{page}"
            html_content = self._make_request(url=page_url, use_selenium=False)
            soup = self._parse_html(html_content)
            # Suppression du debug HTML
            if not soup:
                break
            found_any = False
            # Cibler les articles dans le container principal
            posts_container = soup.find(class_=re.compile(r"elementor-posts-container"))
            if not posts_container:
                break
            for article in posts_container.find_all(class_=re.compile(r"elementor-post ")):
                # Titre et lien
                title_tag = article.find(class_=re.compile(r"elementor-post__title"))
                if not title_tag:
                    continue
                a = title_tag.find('a', href=True)
                if not a:
                    continue
                title = a.get_text(strip=True)
                link = a['href']
                if link in seen_links:
                    continue
                seen_links.add(link)
                # Date
                date_str = None
                meta = article.find(class_=re.compile(r"elementor-post__meta-data"))
                if meta:
                    date_span = meta.find(class_=re.compile(r"elementor-post-date"))
                    if date_span:
                        date_str = date_span.get_text(strip=True)
                if not date_str:
                    print(f"Avertissement: Date non trouvée pour '{title}'. Article ignoré.")
                    continue
                try:
                    article_date = datetime.strptime(date_str, "%B %d, %Y").replace(tzinfo=timezone.utc)
                except Exception:
                    print(f"Avertissement: Mauvais format de date '{date_str}' pour '{title}'. Article ignoré.")
                    continue
                if article_date < date_limite:
                    return articles
                found_any = True
                content = self._extract_article_content(link)
                articles.append({
                    'title': title,
                    'link': link,
                    'date': article_date.isoformat(),
                    'content': content
                })
            if not found_any:
                break
            page += 1
        return articles
