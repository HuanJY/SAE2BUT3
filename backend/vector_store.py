import faiss
import numpy as np
from config import Config
from langchain_huggingface import HuggingFaceEmbeddings
import torch
from langchain.vectorstores import FAISS as LangchainFAISS
from langchain.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import FAISS 


# embeddings (pareil que dans llm.py)
EMBEDDING_MODEL_NAME = "antoinelouis/french-me5-small"
device = "cuda" if torch.cuda.is_available() else "cpu"
embedding_model = HuggingFaceEmbeddings( 
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": device},
    encode_kwargs={"normalize_embeddings": True}
)

from langchain_community.vectorstores import FAISS as LangFAISS

_faiss_singleton = None

def _get_faiss():
    global _faiss_singleton
    if _faiss_singleton is None:
        _faiss_singleton = LangFAISS.load_local(
            Config.FAISS_PATH,
            embeddings=embedding_model,
            distance_strategy=DistanceStrategy.COSINE,
            allow_dangerous_deserialization=True
        )
    return _faiss_singleton

def query_faiss(question: str, top_k: int = Config.DOCUMENT_CONTEXTS_PER_RESPONSE):
    vs = _get_faiss()
    return vs.similarity_search(question, k=top_k)

