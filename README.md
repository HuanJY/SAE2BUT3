# SAE2BUT3
Projet : Implémentation d'un chatbot

## Configuration

Mettez vos clés API dans `backend/config.py`

```
HUGGINGFACEHUB_API_TOKEN = 'A_REMPLIR' # Mettez votre propre clé API
DEEPINFRA_API_TOKEN = 'vMahmKvbdG5GXqsoxuY9DojTJHpewp1C'
```

La clé DEEPINFRA est déjà fournie, et est utilisée pour l'embeddings des fichiers PDFs. L'utilisation est limitée donc une fois l'embeddings fait, ne vous amusez pas à le recalculer 50 fois.

Les embeddings ChromaDB sont déjà fournis.
