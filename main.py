# Fichier : main.py

import json
import time
from scrapers.towards_data_science_scraper import TowardsDataScienceScraper
from scrapers.mistral_ai_scraper import MistralAIScraper
from scrapers.openai_scraper import OpenAIScraper
from scrapers.gemini_scraper import GeminiScraper # Import de la nouvelle classe

def save_articles_to_file(articles, filename='veille_ai.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"\nLes articles ont été sauvegardés dans le fichier '{filename}'.")

def main():
    urls_to_scrape = {
        "tds": [
            #"https://towardsdatascience.com/tag/llm-applications/",
            #"https://towardsdatascience.com/tag/llm/",
            #"https://towardsdatascience.com/tag/ai-agent/",
        ],
        "mistral": [
            #"https://mistral.ai/news"
        ],
        "openai": [
            #"https://openai.com/news/"
        ],
        "gemini": [
            "https://gemini.google/latest-news/"
        ]
    }
    
    all_articles = []
    
    for url in urls_to_scrape["tds"]:
        print(f"\nDébut du scraping de Towards Data Science : {url}...")
        scraper = TowardsDataScienceScraper(url)
        articles_from_site = scraper.scrape()
        all_articles.extend(articles_from_site)
        time.sleep(5) 

    for url in urls_to_scrape["mistral"]:
        print(f"\nDébut du scraping de Mistral AI : {url}...")
        scraper = MistralAIScraper(url)
        articles_from_site = scraper.scrape()
        all_articles.extend(articles_from_site)
        time.sleep(5)

    for url in urls_to_scrape["openai"]:
        print(f"\nDébut du scraping d'OpenAI : {url}...")
        scraper = OpenAIScraper(url)
        articles_from_site = scraper.scrape()
        all_articles.extend(articles_from_site)
        time.sleep(5)

    # Ajout du scraper pour Gemini
    for url in urls_to_scrape["gemini"]:
        print(f"\nDébut du scraping de Gemini : {url}...")
        scraper = GeminiScraper(url)
        articles_from_site = scraper.scrape()
        all_articles.extend(articles_from_site)
        time.sleep(5)
    
    if all_articles:
        all_articles.sort(key=lambda x: x.get('date', '0'), reverse=True)
        save_articles_to_file(all_articles)
    else:
        print("Aucun article récent trouvé sur toutes les pages. Le fichier n'a pas été créé.")

if __name__ == "__main__":
    main()