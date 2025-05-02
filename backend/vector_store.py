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
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
embedding_model = HuggingFaceEmbeddings( 
    model_name=EMBEDDING_MODEL_NAME,
    multi_process=True,
    model_kwargs={"device": device},
    encode_kwargs={"normalize_embeddings": True}
)



def query_faiss(question: str, top_k: int = Config.DOCUMENT_CONTEXTS_PER_RESPONSE): #question : requete dans le moteur de recherche du coup et top_k = nb des res pertinents  qu'on récup et' défini dans DOCUMENT_CONTEXTS_PER_RESPONSE
    vs = LangchainFAISS.load_local(  #on charge l'index
        Config.FAISS_PATH,
        embeddings=embedding_model,
        distance_strategy=DistanceStrategy.COSINE,
        allow_dangerous_deserialization=True
    )
    docs = vs.similarity_search(question, k=top_k)  #exec une recherche de similarité sur une question
    return docs 

