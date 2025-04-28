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

#DOCSTORE_PATH = Config.DOCSTORE_PATH          # "faiss_docstore.json"
INDEX_PATH    = Config.FAISS_PATH             # "faiss_index"

def _hash64(id_str: str) -> int: #pour convertir un texte en id
    return int(hashlib.md5(id_str.encode()).hexdigest()[:16], 16) & 0x7FFF_FFFF_FFFF_FFFF

# def _load_docstore():
#     if os.path.exists(DOCSTORE_PATH):
#         with open(DOCSTORE_PATH, "r", encoding="utf-8") as f:
#             return json.load(f)
#     raise RuntimeError("Docstore introuvable : exécute download_all_pdfs d’abord")

# def create_faiss_index(chunks):
#     texts = [c.page_content for c in chunks]                     # ► list, pas string
#     vectors = np.asarray(embedding_model.embed_documents(texts),
#                          dtype="float32")
#     ids = np.asarray([_hash64(c.metadata["id"]) for c in chunks],
#                      dtype="int64")

#     index = faiss.IndexIDMap(faiss.IndexFlatL2(vectors.shape[1]))
#     index.add_with_ids(vectors, ids)
#     return index

# fonction de recherche FAISS (le query_chroma dans llm.py)
#transforme la question en vecteur + cherche dans FAISS les vecteurs les plus proches 

Il retourne les textes associés.


def query_faiss(question: str, top_k: int = Config.DOCUMENT_CONTEXTS_PER_RESPONSE): #question : requete dans le moteur de recherche du coup et top_k = nb des res pertinents  qu'on récup et' défini dans DOCUMENT_CONTEXTS_PER_RESPONSE
    vs = LangchainFAISS.load_local(  #on charge l'index
        Config.FAISS_PATH,
        embeddings=embedding_model,
        distance_strategy=DistanceStrategy.COSINE,
        allow_dangerous_deserialization=True
    )
    docs = vs.similarity_search(question, k=top_k)  #exec une recherche de similarité sur une question
    return [d.page_content for d in docs]



# chargement de l'index FAISS
# def save_faiss_index(index):
#     faiss.write_index(index, INDEX_PATH)

def load_faiss_index():
    return faiss.read_index(INDEX_PATH)