import os
from config import Config
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema.document import Document
from utils import HFAPIEmbeddingFunction

# Paths
files = [
    "https://bonentrepreneur.wordpress.com/wp-content/uploads/2012/01/lessentiel-de-la-finance-c3a0-lusage-des-managers.pdf",
    "https://www.flornoyferri.com/wp-content/uploads/2024/06/Guide-Pratique-pour-un-investissement-integral.pdf",
    "https://avenuedesinvestisseurs.fr/wp-content/uploads/2022/01/Guide-epargnant-ADI.pdf",
    "https://lautorite.qc.ca/fileadmin/tesaffaires/Programme_education_financiere/INVESTIR-prof_fr.pdf",
    "https://acpr.banque-france.fr/system/files/import/acpr/medias/documents/20210326_revue_acpr_esg_disclosure.pdf",
    "https://www.inc-conso.fr/sites/default/files/pdf_abonne/1278-sec__financiere_175.pdf"
]

def download_all_pdfs(embedding_model):
    os.makedirs("finance_pdfs", exist_ok=True)

    # Function to download PDF file with error handling and retries
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

    # Download all PDFs
    for url in files:
        file_name = url.split('/')[-1]
        file_path = os.path.join("finance_pdfs", file_name)
        if not os.path.exists(file_path):
            download_pdf(url, file_path)
    
    load_all_pdfs(embedding_model)

def chroma_get_indexed_filenames():
    # Récupérer les noms de fichiers déjà indexés
    chroma_db = Chroma(
        #persist_directory=Config.CHROMA_PATH, embedding_function=embedding_model
        persist_directory=Config.CHROMA_PATH, embedding_function=HFAPIEmbeddingFunction()
    )
    existing_items = chroma_db.get(include=["metadatas"], limit=100000)

    indexed_filenames = set()
    for meta in existing_items["metadatas"]:
        source = meta.get("source", "")
        filename = source.split("/")[-1]
        if filename:
            indexed_filenames.add(filename)

    return indexed_filenames

def load_all_pdfs(embedding_model):
    from langchain_community.document_loaders import PyPDFDirectoryLoader
    
    # Load PDFs (further processing if needed)
    # Load pdf
    loader = PyPDFDirectoryLoader("./finance_pdfs/")
    docs_before_split = loader.load()

    # Check already indexed files, and skip them
    indexed_filenames = chroma_get_indexed_filenames()
    filtered_docs = [doc for doc in docs_before_split if doc.metadata.get("source", "").split("/")[-1] not in indexed_filenames]
    if not filtered_docs:
        print("Aucun nouveau fichier à charger depuis ./finance_pdfs/")
        return []

    avg_doc_length = lambda docs: sum([len(doc.page_content) for doc in filtered_docs])//len(docs)
    avg_char_before_split = avg_doc_length(filtered_docs)
    print(f'Before split, there were {len(docs_before_split)} documents loaded, with average characters equal to {avg_char_before_split}.')
    
    
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 512, # max input lenght of our tokenizer
        chunk_overlap  = 512 // 10,
    )
    # Return list
    docs_after_split = text_splitter.split_documents(filtered_docs)
    avg_char_after_split = avg_doc_length(docs_after_split)
    print(f'After split, there were {len(docs_after_split)} documents (chunks), with average characters equal to {avg_char_after_split} (average chunk length).')
    
    add_to_chroma(docs_after_split, embedding_model)
    
    return docs_after_split
    
def add_to_chroma(chunks: list[Document], embedding_model):
    # Load the existing database.
    chroma_db = Chroma(
        #persist_directory=Config.CHROMA_PATH, embedding_function=embedding_model
        persist_directory=Config.CHROMA_PATH, embedding_function=HFAPIEmbeddingFunction()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = chroma_db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"ChromaDB: Nombre de documents existants dans la base de données : {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"ChromaDB: Ajout de {len(new_chunks)} nouveaux documents")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        current_i = 0
        STEP_SIZE = Config.MAX_EMBEDDING_BATCH_SIZE
        while current_i < len(new_chunks):
            end_i = current_i + STEP_SIZE
            if end_i > len(new_chunks):
                end_i = len(new_chunks)
            chroma_db.add_documents(new_chunks[current_i:end_i], ids=new_chunk_ids[current_i:end_i])
            print(f"ChromaDB: Progression: {end_i}/{len(new_chunks)} documents")
            current_i += STEP_SIZE
        #chroma_db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("ChromaDB: Aucun nouveau document à ajouter")
    
def calculate_chunk_ids(chunks):
    # This will create IDs like "data/resume.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks
