# Fichier : main.py

import json
import time
from scrapers.towards_data_science_scraper import TowardsDataScienceScraper
from scrapers.mistral_ai_scraper import MistralAIScraper
from scrapers.openai_scraper import OpenAIScraper
from scrapers.gemini_scraper import GeminiScraper
from scrapers.langchain_scraper import LangChainScraper 
from scrapers.ollama_scraper import OllamaScraper

def save_articles_to_file(articles, filename='veille_ai.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"\nLes articles ont été sauvegardés dans le fichier '{filename}'.")

def main():
    urls_to_scrape = {
        "tds": [
            "https://towardsdatascience.com/tag/llm-applications/",
            "https://towardsdatascience.com/tag/llm/",
            "https://towardsdatascience.com/tag/ai-agent/",
        ],
        "mistral": [
            "https://mistral.ai/news"
        ],
        "openai": [
            "https://openai.com/news/"
        ],
        "gemini": [
            "https://gemini.google/latest-news/"
        ],
        "langchain": [
            "https://blog.langchain.com/"
        ],
        "ollama": [
            "https://ollama.com/blog"
        ]
    }

    scrapers = {
        "tds": TowardsDataScienceScraper,
        "mistral": MistralAIScraper,
        "openai": OpenAIScraper,
        "gemini": GeminiScraper,
        "langchain": LangChainScraper,
        "ollama": OllamaScraper
    }

    all_articles = []

    for source, urls in urls_to_scrape.items():
        ScraperClass = scrapers[source]
        for url in urls:
            print(f"\nDébut du scraping de {source.capitalize()} : {url}...")
            scraper = ScraperClass(url)
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