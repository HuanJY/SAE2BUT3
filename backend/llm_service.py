from vector_store import embedding_model, query_faiss
from openai import OpenAI
from config import Config
from models import db, Message

client = OpenAI(
    api_key=Config.DEEPINFRA_API_TOKEN,
    base_url="https://api.deepinfra.com/v1/openai"
)

def generate_answer(question: str, chat, top_k: int = 3) -> Message:
    # 1. contexte
    docs = query_faiss(question, top_k)
    context = "\n\n".join(d.page_content for d in docs)

    # 2. prompt complet
    prompt = (
        "CONTEXTE (documents internes) :\n"
        f"{context}\n\n"
        f"Question : {question}\n\n"
         "Utilise UNIQUEMENT les éléments de CONTEXTE suivants pour répondre à la question finale. Veuille à suivre les règles suivantes :\n 1. Si tu trouves la réponse, rédige-la de manière semi-longue, en une dixaine de phrases maximum.\n 2. Tes seules connaissances sont le contexte donné. Si tu ne trouves pas la réponse UNIQUEMENT dans le CONTEXTE qui t'es donné, dis simplement : « Je n'arrive pas à trouver de réponse finale, car je n'ai pas connaissance de ce sujet. », et ne dis rien d'autre après.\n 3. Ce n'est pas grave si tu trouves pas la réponse."
    )

    # 3. appel LLM (Mistral 7B via DeepInfra)
    answer = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content

    # 4. persiste la réponse/sauv en bdd
    msg = Message(chat_id=chat.chat_id, content=answer, is_user=False,
                  context=context)
    db.session.add(msg)
    db.session.commit()
    return msg
