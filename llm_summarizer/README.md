# LLM Summarizer

Ce dossier contient un script Python pour résumer automatiquement les articles collectés dans `veille_ai.json` à l'aide de l'API OpenAI.

## Utilisation

1. Installez la dépendance :
   ```bash
   pip install openai
   ```
2. Exportez votre clé API OpenAI dans la variable d'environnement `OPENAI_API_KEY`.
3. Exécutez le script :
   ```bash
   python summarize_articles.py
   ```

Le fichier `veille_ai_summaries.json` sera généré avec les résumés.

## Personnalisation
- Modifiez le modèle ou le prompt dans `summarize_articles.py` si besoin.
