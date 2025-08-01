from scrapers.towards_data_science_scraper import TowardsDataScienceScraper

# URL à scrapper
tds_url = "https://towardsdatascience.com/tag/llm-applications/"

# Instancier le scraper pour Towards Data Science
tds_scraper = TowardsDataScienceScraper(tds_url)

print(f"Début du scraping de {tds_url}...")
articles = tds_scraper.scrape()

# Afficher les résultats
print("\nArticles trouvés :")
for article in articles:
    print(f"- Titre: {article['title']}\n  Lien: {article['link']}")
    print("-" * 20)