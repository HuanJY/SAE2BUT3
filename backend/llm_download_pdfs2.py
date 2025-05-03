import os, time, json, hashlib
import faiss, numpy as np
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from config import Config
from langchain.vectorstores import FAISS as LangchainFAISS
from langchain.vectorstores.utils import DistanceStrategy
from langchain_community.vectorstores import FAISS

FILES = [
    "https://bonentrepreneur.wordpress.com/wp-content/uploads/2012/01/lessentiel-de-la-finance-c3a0-lusage-des-managers.pdf",
    "https://www.flornoyferri.com/wp-content/uploads/2024/06/Guide-Pratique-pour-un-investissement-integral.pdf",
    "https://avenuedesinvestisseurs.fr/wp-content/uploads/2022/01/Guide-epargnant-ADI.pdf",
    "https://lautorite.qc.ca/fileadmin/tesaffaires/Programme_education_financiere/INVESTIR-prof_fr.pdf",
    "https://acpr.banque-france.fr/system/files/import/acpr/medias/documents/20210326_revue_acpr_esg_disclosure.pdf",
    "https://www.inc-conso.fr/sites/default/files/pdf_abonne/1278-sec__financiere_175.pdf",
]

# DOCSTORE_PATH = Config.DOCSTORE_PATH          # pour stock les id et le dico des chunks 
# INDEX_PATH    = Config.FAISS_PATH            # pour stock les index

def download_all_pdfs(embedding_model): #Pareil que dans le script chromadb
    os.makedirs("finance_pdfs", exist_ok=True)

    def download_pdf(url, file_path, retries=3, delay=5):
        for attempt in range(retries):
            try:
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req) as response, open(file_path, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"Successfully downloaded {file_path}")
                return
            except HTTPError as e:
                print(f"HTTP Error: {e.code} for {url}. Retrying in {delay} seconds...")
            except URLError as e:
                print(f"URL Error: {e.reason} for {url}. Retrying in {delay} seconds...")
            except Exception as e:
                print(f"Unexpected error: {e} for {url}. Retrying in {delay} seconds...")

            time.sleep(delay)

        print(f"Failed to download {url} after {retries} attempts.")

    for url in FILES:
        file_path = os.path.join("finance_pdfs", url.split("/")[-1])
        if not os.path.exists(file_path):
            download_pdf(url, file_path)

    load_all_pdfs(embedding_model)

# on gère la logique faiss que chromadb fasait automatiquement ci-dessous (chromadb stocke tout, recherche le chunk, identifie le chunk indexé etc.)
# def _load_docstore(): #contient id texte et metadonnés
#     if os.path.exists(DOCSTORE_PATH):
#         with open(DOCSTORE_PATH, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return {}

# def _save_docstore(store: dict): 
#     with open(DOCSTORE_PATH, "w", encoding="utf-8") as f:
#         json.dump(store, f, ensure_ascii=False, indent=2)

# def _hash64(id_str: str) -> int:
#     return int(hashlib.md5(id_str.encode()).hexdigest()[:16], 16) & 0x7FFF_FFFF_FFFF_FFFF

# def calculate_chunk_ids(chunks: list[Document]): 
#     last_page = None
#     idx = 0
#     for c in chunks:
#         src, page = c.metadata.get("source"), c.metadata.get("page")
#         page_id = f"{src}:{page}"
#         idx = idx + 1 if page_id == last_page else 0
#         c.metadata["id"] = f"{page_id}:{idx}"
#         last_page = page_id
#     return chunks


#charge+découpe+filtre
#charge tous les PDF présents localement.
def load_all_pdfs(embedding_model):
    loader   = PyPDFDirectoryLoader("./finance_pdfs/")
    raw_docs = loader.load()

    # identifie ceux qui ne sont pas encore indexés
    if os.path.exists(Config.FAISS_PATH):
        vs = LangchainFAISS.load_local( #charge l'index 
            Config.FAISS_PATH,
            embeddings=embedding_model,
            distance_strategy=DistanceStrategy.COSINE,
            allow_dangerous_deserialization=True #j'ai mis ce paramètre sinon j'ai un message d'erreur sur la sécurité
        )
        #existing_sources ensembke de fichiers deja traites.
        existing_sources = {doc.metadata.get("source") for doc in vs.docstore._dict.values()} #vs.docstore._dict est un dico qui contient tous les documents déjà indexés
        #.metadata.get("source") pour récupèrer le PDF source de chaque chunk
    else: 
        vs = None
        existing_sources = set()

    new_docs = [d for d in raw_docs if d.metadata["source"] not in existing_sources] #on garde que les docs dont le champ "source" n’est pas déjà dans l’index
    if not new_docs:
        print("aucun nouveau pdf à indexer.")
        return

    # découpe les documents avec RecursiveCharacterTextSplitter (qu'on a vu en cours)
    splitter = RecursiveCharacterTextSplitter(chunk_size=Config.SPLITTER_CHUNK_SIZE, chunk_overlap=Config.SPLITTER_CHUNK_SIZE // 10)
    chunks   = splitter.split_documents(new_docs)

    # on index avec faiss via langchain
    if vs is None:
        vs = LangchainFAISS.from_documents(
            chunks,
            embedding_model,
            distance_strategy=DistanceStrategy.COSINE
        )
    else:
        vs.add_documents(chunks)

    vs.save_local(Config.FAISS_PATH) 
    print(f"{len(chunks)} chunks ajoutés. Index mis à jour !")



# indexation FAISS
# def add_to_faiss(chunks: list[Document], embedding_model):
#     store = _load_docstore()
#     new_chunks = [c for c in chunks if c.metadata["id"] not in store]
#     if not new_chunks:
#         print("Index FAISS déjà à jour.")
#         return

#     texts = [c.page_content for c in new_chunks]
#     vectors = np.asarray(embedding_model.embed_documents(texts), dtype="float32")
#     ids = np.asarray([_hash64(c.metadata["id"]) for c in new_chunks], dtype="int64")

#     # charge ou crée l’index
#     if os.path.exists(INDEX_PATH):
#         index = faiss.read_index(INDEX_PATH)
#     else:
#         index = faiss.IndexIDMap(faiss.IndexFlatL2(vectors.shape[1]))

#     index.add_with_ids(vectors, ids)
#     faiss.write_index(index, INDEX_PATH)
#     print(f"{len(new_chunks)} nouveaux chunks ajoutés à FAISS.")

#     # maj docstore
#     for c in new_chunks:
#         store[c.metadata["id"]] = {
#             "text": c.page_content,
#             "metadata": c.metadata
#         }
#     _save_docstore(store)
