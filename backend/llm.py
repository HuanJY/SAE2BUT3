from config import Config
import os
os.environ['HUGGINGFACEHUB_API_TOKEN'] = Config.HUGGINGFACEHUB_API_TOKEN

# Get embedder
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain_community.vectorstores.utils import DistanceStrategy
import torch
#from langchain.vectorstores import FAISS
#import faiss
from langchain_chroma import Chroma
from utils import HFAPIEmbeddingFunction
from openai import OpenAI
from sqlalchemy import desc

# Embedder
EMBEDDING_MODEL_NAME = "antoinelouis/french-me5-small" # OLD: almanach/camembert-base --- OLD: thenlper/gte-small
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    multi_process=True,
    model_kwargs={"device": device},
    encode_kwargs={"normalize_embeddings": True},  # set True for cosine similarity
)


def query_chroma(query_text: str):
    chroma_db = Chroma(
        #persist_directory=Config.CHROMA_PATH, embedding_function=embedding_model
        persist_directory=Config.CHROMA_PATH, embedding_function=HFAPIEmbeddingFunction()
    )
    results = chroma_db.similarity_search_with_score(query_text, k=Config.DOCUMENT_CONTEXTS_PER_RESPONSE)
    return results


"""
docs_after_split = load_all_pdfs()

# Save all documents in the database
KNOWLEDGE_VECTOR_DATABASE = FAISS.from_documents(
    docs_after_split, embedding_model, distance_strategy=DistanceStrategy.COSINE
)

# Save embeddings
KNOWLEDGE_VECTOR_DATABASE.save_local("faiss_index")
"""


# ---

from models import db, User, Chat, Message

from huggingface_hub import InferenceClient
API_URL="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
# API_URL = "https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud"
client = InferenceClient(API_URL + "/v1/chat/completions", token=Config.HUGGINGFACEHUB_API_TOKEN)

def get_system_prompt():
    return {"role": "system", "content": """Utilise UNIQUEMENT les éléments de CONTEXTE suivants pour répondre à la question finale. Veuille à suivre les règles suivantes :
    1. Si tu trouves la réponse, rédige-la de manière semi-longue, en une dixaine de phrases maximum.
    2. Tes seules connaissances sont le contexte donné. Si tu ne trouves pas la réponse UNIQUEMENT dans le CONTEXTE qui t'es donné, dis simplement : « Je n'arrive pas à trouver de réponse finale, car je n'ai pas connaissance de ce sujet. », et ne dis rien d'autre après.
    3. Ce n'est pas grave si tu trouves pas la réponse."""}

"""
def get_message_history_list(chat):
    # deprecated
    historique = []
    historique.append(get_system_prompt())
    
    for message in chat.messages:
        if historique[-1]["role"] == "user":
            historique.append({"role": "assistant", "content": message.content})
        else:
            historique.append({"role": "user", "content": message.content})
    
    return historique
"""

def get_message_history_context_summary(chat):
    last_user_messages = (
        db.session.query(Message)
        .filter(Message.chat_id == chat.chat_id, Message.is_user == False)
        .order_by(desc(Message.create_time))
        .limit(1)
        .all()
    )
    return [msg.context for msg in last_user_messages]

def obtenir_reponse(question, chat):
    #historique = get_message_history_list(chat)
    historique = []
    historique.append(get_system_prompt())
    
    """
    retrieved_docs = KNOWLEDGE_VECTOR_DATABASE.similarity_search(query=user_query, k=5)

    retrieved_docs_text = [doc.page_content for doc in retrieved_docs]
    """
    print("Retrieving documents")
    retrieved_docs_text = [doc.page_content for doc, _score in query_chroma(question)]
    print("Docs retrieved")
    new_context = "\nDocuments extraits:\n\n"
    new_context_data = "".join([doc + "\n\n" for i, doc in enumerate(retrieved_docs_text)])
    
    print("Fetching old context")
    old_contexts = get_message_history_context_summary(chat)
    if old_contexts:
        new_context += "\n\n".join(old_contexts)
        new_context += "\n\n"
    
    new_context += new_context_data

    # Ajouter le prompt à l'historique, ou l'override si déjà existant
    new_message = {
        "role": "user",
        "content": f"CONTEXTE: {new_context}\n\nQuestion: {question}\n\nRéponse utile:"
    }
    print(new_context)
    if historique[-1]["role"] == "user":
        historique[-1] = new_message
    else:
        historique.append(new_message)

    #print("[LOG] Embeddings effectué, prédiction de la réponse...")

    #print(historique)

    # Demander la prédiction au modèle
    print("Predicting response")

    if Config.LLM_USE == "huggingface":
        reponse = client.chat_completion(historique)
        reponse = reponse.choices[0].message.content
    elif Config.LLM_USE == "deepinfra":
        # Create an OpenAI client with your deepinfra token and endpoint
        openai = OpenAI(
            api_key=Config.DEEPINFRA_API_TOKEN,
            base_url="https://api.deepinfra.com/v1/openai",
        )

        chat_completion = openai.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=historique,
        )

        reponse = chat_completion.choices[0].message.content
    else:
        raise Exception("No valid Config.LLM_USE set")

    print("Response predicted")

    # Afficher la réponse
    print(f"Réponse prédite : {reponse}")

    # Ajouter la réponse à l'historique pour le suivi
    historique.append({
        "role": "assistant",
        "content": reponse
    })
    
    message = Message(content=reponse, chat_id=chat.chat_id, context=new_context_data, is_user=False)
    db.session.add(message)
    db.session.commit()

    return {'message_id': message.message_id, 'content': message.content, 'is_user': False, 'create_time': message.create_time, 'context': message.context}

#output = client.chat_completion([{"role": "user", "content": "who is the president of France?"}])
#output = client.chat_completion([{"role": "user", "content": "who is the president of France?"}])

#print(output.choices[0].message.content)
