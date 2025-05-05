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

## Execution

**Windows :**

- Lancer `create venv.bat` (la première fois uniquement)
  - Attendre que la création du venv soit terminé. Puis lancer `open venv.bat` et run `pip install -r requirements.txt`
- Lancer `open venv.bat` 2 fois
  - Dans la première fenêtre, faire : 
    - `cd backend`
    - `py app.py`
  - Attendre le lancement du backend... Dans la deuxième fenêtre, faire :
    - `cd frontend`
    - `streamlit run EcoChatbot.py`

**Linux :**

Instructions à venir
