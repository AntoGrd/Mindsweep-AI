import os
import json
from openai_compat import chat_completion

def summarize_all_articles(articles, model="gpt-5-mini-2025-08-07"):
    # Construire un prompt qui liste les titres et liens, puis demande un résumé global
    refs = "\n".join([
        f"- {a.get('title', 'Sans titre')} ({a.get('link', '')})" for a in articles
    ])
    contents = "\n\n".join([
        f"{a.get('title', 'Sans titre')} : {a.get('content', '')}" for a in articles
    ])
    prompt = (
        "Bonjour,\n"
        "En tant que journaliste spécialisé dans les domaines de la data et de l'intelligence artificielle pour un cabinet de conseil, votre mission est de rédiger notre veille technologique hebdomadaire. Ce résumé, conçu pour être envoyé par e-mail à l'ensemble des consultants, doit leur permettre d'être informés rapidement et efficacement des dernières évolutions.\n"
        "Vous disposez d'un ensemble d'articles récents (moins de 7 jours).\n"
        "Rédigez un résumé d'une page maximum, au ton professionnel et percutant. L'objectif est de synthétiser les informations clés et les tendances majeures de la semaine, comme le ferait un journaliste.\n"
        "Structurez votre résumé de manière à ce qu'il soit facilement lisible et scannable. Utilisez des sous-parties pertinentes, telles que :\n"
        "- **À la Une : Modèles et Améliorations Majeures**\n"
        "- **Innovations et Applications Pratiques**\n"
        "- **Collaborations et Partenariats Stratégiques**\n"
        "- **Outils et Concepts pour les Développeurs et Data Scientists**\n"
        "Organisez les informations de manière logique en citant les titres et les liens des articles pour chaque point important. Chaque point doit être concis pour capter rapidement l'attention du lecteur.\n"
        "Terminez le résumé par une brève section 'Pour aller plus loin' qui invite les consultants à explorer les sources originales.\n"
        f"Références :\n{refs}\n\nContenus :\n{contents}"
    )
    response = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        #max_tokens=max_tokens,
        #temperature=0.5,
    )
    return response

def main(input_json="../veille_ai.json", output_md="../veille_ai_summaries.md"):
    with open(input_json, encoding="utf-8") as f:
        articles = json.load(f)
    if not articles:
        print("Aucun article à résumer.")
        return
    try:
        summary = summarize_all_articles(articles)
    except Exception as e:
        summary = f"Erreur lors du résumé global : {e}"
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Résumé global sauvegardé dans {output_md}")

if __name__ == "__main__":
    main()
