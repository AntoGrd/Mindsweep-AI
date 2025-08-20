import json
from llm_summarizer.summarize_articles import summarize_all_articles

with open("veille_ai.json", encoding="utf-8") as f:
    articles = json.load(f)

summary = summarize_all_articles(articles)

with open("veille_ai_summaries.html", "w", encoding="utf-8") as f:
    f.write(summary)

print("Résumé HTML généré dans veille_ai_summaries.html")
