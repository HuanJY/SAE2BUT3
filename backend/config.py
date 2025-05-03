import os

class Config:
    SECRET_KEY = 'IY4AaZAmVdNQHGTssARb3yutVbd27hKT'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/sae_economy_db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///backend.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HUGGINGFACEHUB_API_TOKEN = 'A_REMPLIR' # Mettez votre propre clé API
    DEEPINFRA_API_TOKEN = 'vMahmKvbdG5GXqsoxuY9DojTJHpewp1C'
    EMBEDDINGS_USE = "huggingface" # 'huggingface'
    LLM_USE = "deepinfra" # 'huggingface' or 'deepinfra'
    LLM_MAX_TOKENS = 500
    LLM_TEMPERATURE = 0.7
    LLM_MAX_PAST_CONTEXTS = 2 # Le nombre de contextes précédents à utiliser pour la prédiction. 2 = passera également le contexte des 2 précédentes questions. Risque de dépassement de fenêtre de contexte si trop élevé.
    CHROMA_PATH = "chroma"
    DOCUMENT_CONTEXTS_PER_RESPONSE = 2 #Combien de documents on récupère pour répondre à une question (Utilisé dans llm.py pour faire des recherches dans FAISS/Chroma)
    MAX_EMBEDDING_BATCH_SIZE = 20 #Nombre max de documents envoyés en une fois pour l’embedding (Utile pour éviter d’envoyer des batchs trop lourds à HuggingFace)
    SPLITTER_CHUNK_SIZE = 512 # Taille d'un chunck pour l'embeddings
    
    FAISS_PATH = "faiss_index" #utilisés pour sauvegarder/charger l'index (pour la recherche sémantique avec LangChain)
    DOCSTORE_PATH = "faiss_docstore.json"

    DEBUG_PRINT = True # Activer pour avoir des print à certaines étapes avec des infos. Utile pour le débuggage.
