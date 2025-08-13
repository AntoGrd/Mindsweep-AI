import openai
import os
import json

def chat_completion(messages, model="gpt-5-mini-2025-08-07"):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        #max_tokens=max_tokens,
        #temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def summarize_all_articles(articles, model="gpt-5-mini-2025-08-07"):
    refs = "\n".join([
        f"- {a.get('title', 'Sans titre')} ({a.get('link', '')})" for a in articles
    ])
    contents = "\n\n".join([
        f"{a.get('title', 'Sans titre')} : {a.get('content', '')}" for a in articles
    ])
    prompt = (
        "Bonjour,\n\n"
        "En tant que journaliste spécialisé dans les domaines de la data et de l'intelligence artificielle pour un cabinet de conseil, votre mission est de rédiger notre veille technologique hebdomadaire. Ce résumé est destiné à être envoyé par e-mail à tous les consultants pour les informer rapidement et efficacement.\n\n"
        "Vous disposez d'un ensemble d'articles récents (moins de 7 jours).\n\n"
        "Pour commencer le mail, rédigez une brève introduction (2 à 3 phrases) qui donne un aperçu des sujets clés abordés dans la veille. Cette introduction doit être percutante, résumant les faits marquants de la semaine. Elle doit donner envie aux consultants de lire la suite pour en savoir plus sur les annonces importantes, les tendances émergentes et les outils phares. Le ton doit être direct et professionnel.\n\n"
        "Rédigez un résumé d'une page maximum, clair et percutant. L'objectif est de synthétiser les informations clés et les tendances majeures de la semaine en adoptant un ton à la fois professionnel et accessible, comme le ferait un bon journaliste.\n\n"
        "Veillez à ce que toutes les phrases soient complètes et grammaticalement correctes, comme dans un article de journal. Évitez le style télégraphique et les raccourcis. Par exemple, écrivez 'pour réaliser une exploration par thématique' plutôt que 'pour exploration thématique', ou 'choisir des métriques' plutôt que 'choisir métriques'.\n"
        "Le résumé doit être suffisamment détaillé pour être informatif en lui-même. Chaque point doit permettre au lecteur d'apprendre quelque chose de concret sur le sujet, sans avoir à consulter l'article d'origine. Les descriptions doivent être vulgarisées, expliquant clairement les concepts techniques pour un non-expert.\n\n"
        "Structurez le résumé avec des titres de sous-parties dynamiques et pertinents :\n"
        "- **À la Une : Modèles et Améliorations Majeures**\n"
        "- **Innovations et Applications Pratiques**\n"
        "- **Collaborations et Partenariats Stratégiques**\n"
        "- **Outils et Concepts pour les Développeurs et Data Scientists**\n\n"
        "Organisez les informations de manière logique. Pour chaque point important, citez le titre de l'article et intégrez le lien discret en hypertexte sur le titre. Chaque phrase doit être complète, bien construite et utiliser une syntaxe correcte (par exemple, \"utile pour anticiper les opportunités\" au lieu de \"utile pour anticiper opportunités\").\n\n"
        "Terminez le résumé en proposant une section 'Pour aller plus loin' qui recommande des lectures ou des actions concrètes par catégorie de profil (ex: 'Pour les data scientists', 'Pour les ML Engineer', 'Pour la Data Analysts', etc..). Ces recommandations doivent être basées sur les articles de la semaine et inciter le consultant à explorer les sujets qui le concernent le plus. La phrase de conclusion doit simplement clore le mail de manière élégante et professionnelle, sans suggérer d'interaction ou de réponse directe.\n\n"
        f"Références :\n{refs}\n\nContenus :\n{contents}"
    )
    response = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        #max_tokens=max_tokens,
        #temperature=0.5,
    )
    return response