# Fichier : scrapers/towards_data_science_scraper.py

from .base_scraper import BaseScraper 

class TowardsDataScienceScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        # Sélecteur pour chaque conteneur d'article (un <li>)
        # Il y a aussi des <li> pour les publicités, donc on filtre
        self.article_selector = 'li.wp-block-post.type-post' 
        # Sélecteur pour le lien et le titre à l'intérieur du conteneur
        self.title_link_selector = 'h2 a' 
        
    def scrape(self):
        html_content = self._make_request()
        soup = self._parse_html(html_content)
        if not soup:
            print("Erreur: Impossible de récupérer ou de parser le contenu HTML.")
            return []
        
        articles = []
        # Trouver tous les conteneurs d'articles avec les bonnes classes
        article_elements = soup.select(self.article_selector)
        
        if not article_elements:
            print("Aucun élément d'article trouvé. Le sélecteur est probablement incorrect.")
            print(f"Sélecteur utilisé : {self.article_selector}")
            return []
            
        for article_elem in article_elements:
            # Chercher le lien et le titre à l'intérieur de chaque article
            title_link_elem = article_elem.select_one(self.title_link_selector)
            
            if title_link_elem:
                title = title_link_elem.get_text(strip=True)
                link = title_link_elem['href']

                # S'assurer que le lien est absolu
                if not link.startswith('http'):
                    link = 'https://towardsdatascience.com' + link
                
                # Le code ci-dessous (pour le résumé) n'est pas nécessaire mais vous pouvez l'ajouter
                # pour extraire le résumé si vous le souhaitez.
                # summary_elem = article_elem.select_one('div.wp-block-post-excerpt p')
                # summary = summary_elem.get_text(strip=True) if summary_elem else 'No summary available.'
                
                articles.append({'title': title, 'link': link})
        
        return articles