# Fichier : scrapers/mistral_ai_scraper.py

from .base_scraper import BaseScraper
from datetime import datetime, timedelta, timezone
import json
import time
import re

class MistralAIScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.content_selector = 'main'

    def _extract_article_content_from_page(self, article_url):
        print(f"  > Récupération du contenu de: {article_url}")
        time.sleep(2)
        html_content = self._make_request(url=article_url)
        soup = self._parse_html(html_content)
        if soup:
            content_element = soup.select_one(self.content_selector)
            if content_element:
                return content_element.get_text(separator='\n', strip=True)
        return "Contenu non trouvé."

    def scrape(self):
        html_content = self._make_request(url=self.url, use_selenium=False)
        soup = self._parse_html(html_content)
        
        if not soup:
            print("Erreur: Impossible de récupérer ou de parser le contenu HTML.")
            return []
        
        posts_data = []

        target_script = None
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'posts' in script.string and 'categories' in script.string:
                target_script = script
                break

        if not target_script:
            print("Erreur: Impossible de trouver la balise script contenant les données des articles.")
            return []
            
        try:
            # L'expression régulière pour extraire le JSON
            match = re.search(r'posts\\":(\[.*?\]),\\"categories\\"', target_script.string, re.DOTALL)
            
            if not match:
                print("Erreur: L'expression régulière n'a pas trouvé de correspondance pour les articles.")
                return []
            
            # La chaîne extraite est le contenu du tableau JSON
            json_str = match.group(1)
            
            # CORRECTION: Le JSON contient des échappements qui doivent être décodés
            # On utilise json.loads() avec decode('unicode_escape') pour gérer les \"
            try:
                # D'abord décoder les échappements unicode
                decoded_json_str = json_str.encode().decode('unicode_escape')
                posts_data = json.loads(decoded_json_str)
            except UnicodeDecodeError:
                # Si le décodage unicode échoue, essayer de remplacer manuellement les échappements
                cleaned_json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
                posts_data = json.loads(cleaned_json_str)

            print(f"Extraction réussie de {len(posts_data)} articles depuis le script.")
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Erreur lors de l'extraction ou du décodage des données JSON : {e}")
            print(f"Extrait JSON problématique: {json_str[:200]}...")  # Afficher les premiers caractères pour debug
            return []
            
        articles = []
        date_limite = datetime.now(timezone.utc) - timedelta(days=7)

        for post in posts_data:
            post_date_str = post.get('date')
            if not post_date_str:
                continue

            try:
                # Parser la date ISO
                article_date = datetime.fromisoformat(post_date_str)
                
                # S'assurer que la date a une timezone (convertir en UTC si nécessaire)
                if article_date.tzinfo is None:
                    article_date = article_date.replace(tzinfo=timezone.utc)
                
            except ValueError:
                print(f"Avertissement : Impossible de parser la date '{post_date_str}'. Article ignoré.")
                continue

            if article_date >= date_limite:
                title = post.get('title', 'Titre non trouvé')
                slug = post.get('slug')
                if not slug:
                    continue
                link = f"https://mistral.ai/news/{slug}"
                
                article_content = self._extract_article_content_from_page(link)

                articles.append({
                    'title': title,
                    'link': link,
                    'date': post_date_str,
                    'content': article_content
                })
        
        return articles