# Fichier : scrapers/towards_data_science_scraper.py

from .base_scraper import BaseScraper
from datetime import datetime, timedelta, timezone
import time 
import re 
class TowardsDataScienceScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.article_selector = 'li.wp-block-post.type-post'
        self.title_link_selector = 'h2 a'
        self.date_selector = 'time'
        # Sélecteur spécifique pour le contenu d'un article sur Towards Data Science
        self.content_selector = 'div.post-content' # C'est une hypothèse, il faudra vérifier.

    def _extract_article_content_from_page(self, article_url):
        """
        Récupère et extrait le contenu textuel d'un article donné.
        """
        print(f"  > Récupération du contenu de: {article_url}")
        # Pause de 2 secondes pour être poli
        time.sleep(2) 
        html_content = self._make_request(url=article_url, use_selenium=True)
        soup = self._parse_html(html_content)
        if soup:
            # Inspection d'une page d'article sur TDS révèle le sélecteur suivant :
            content_div = soup.find('div', class_='wp-block-post-content')
            if content_div:
                # Retourne le texte de l'élément en enlevant les balises superflues
                return content_div.get_text(separator='\n', strip=True)
        return "Contenu non trouvé."

    def scrape(self):
        html_content = self._make_request(use_selenium=True)
        soup = self._parse_html(html_content)
        if not soup:
            print("Erreur: Impossible de récupérer ou de parser le contenu HTML.")
            return []
        
        articles = []
        article_elements = soup.select(self.article_selector)
        
        if not article_elements:
            print("Aucun élément d'article trouvé. Le sélecteur est probablement incorrect.")
            print(f"Sélecteur utilisé : {self.article_selector}")
            return []
            
        date_limite = datetime.now(timezone.utc) - timedelta(days=7)

        for article_elem in article_elements:
            title_link_elem = article_elem.select_one(self.title_link_selector)
            date_elem = article_elem.select_one(self.date_selector)
            
            if title_link_elem and date_elem and 'datetime' in date_elem.attrs:
                title = title_link_elem.get_text(strip=True)
                link = title_link_elem['href']
                
                if not link.startswith('http'):
                    link = 'https://towardsdatascience.com' + link

                try:
                    article_date = datetime.fromisoformat(date_elem['datetime'])
                except ValueError:
                    print(f"Avertissement : Impossible de parser la date '{date_elem['datetime']}'. Article ignoré.")
                    continue

                if article_date >= date_limite:
                    # Ici, on va appeler la nouvelle méthode pour récupérer le contenu de l'article
                    article_content = self._extract_article_content_from_page(link)
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'date': date_elem['datetime'],
                        'content': article_content
                    })
                else:
                    print(f"Article '{title}' a plus de 7 jours. Fin du scraping de TDS.")
                    break
        return articles