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
    CHROMA_PATH = "chroma"
    DOCUMENT_CONTEXTS_PER_RESPONSE = 2 #Combien de documents on récupère pour répondre à une question (Utilisé dans llm.py pour faire des recherches dans FAISS/Chroma)
    MAX_EMBEDDING_BATCH_SIZE = 20 #Nombre max de documents envoyés en une fois pour l’embedding (Utile pour éviter d’envoyer des batchs trop lourds à HuggingFace)
    
    FAISS_PATH = "faiss_index" #utilisés pour sauvegarder/charger l'index (pour la recherche sémantique avec LangChain)
    DOCSTORE_PATH = "faiss_docstore.json"
