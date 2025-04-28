import jwt
from datetime import datetime, timedelta, timezone
from config import Config
from openai import OpenAI

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

import requests

#API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-mpnet-base-v2"

def query_embedding(texts):
    if Config.HUGGINGFACEHUB_API_TOKEN and Config.EMBEDDINGS_USE == "huggingface":
        API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        headers = {"Authorization": f"Bearer {Config.HUGGINGFACEHUB_API_TOKEN}"}

        body = {
            "inputs": texts
        }
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        return response.json()
    elif Config.DEEPINFRA_API_TOKEN:
        pass

class HFAPIEmbeddingFunction:
    def embed_documents(self, texts):
        return query_embedding(texts)

    def embed_query(self, text):
        return query_embedding([text])[0]


