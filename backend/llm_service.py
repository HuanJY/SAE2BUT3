from vector_store import embedding_model, query_faiss
from openai import OpenAI
from config import Config
from models import db, Message
from sqlalchemy import desc

client = OpenAI(
    api_key=Config.DEEPINFRA_API_TOKEN,
    base_url="https://api.deepinfra.com/v1/openai"
)

def get_message_history_context_summary(chat):
    last_user_messages = (
        db.session.query(Message)
        .filter(Message.chat_id == chat.chat_id, Message.is_user == False)
        .order_by(desc(Message.create_time))
        .limit(Config.LLM_MAX_PAST_CONTEXTS)
        .all()
    )
    return [msg.context for msg in last_user_messages]

def generate_answer(question: str, chat, top_k: int = -1) -> Message:
    # 1. contexte
    if Config.DEBUG_PRINT: print("Retrieving documents to create the new context...")
    if top_k == -1:
        docs = query_faiss(question)
    else:
        docs = query_faiss(question, top_k)
    context = "\nDocuments extraits:\n\n"
    new_context = "\n\n".join(d.page_content for d in docs)

    # 2. ancien contexte
    if Config.DEBUG_PRINT: print("Fetching old context...")
    old_contexts = get_message_history_context_summary(chat)
    if old_contexts:
        context += "\n\n".join(old_contexts)
        context += "\n\n"
    
    context += new_context

    # 3. Build les messages
    def get_system_prompt():
        return {"role": "system", "content": "Utilise UNIQUEMENT les éléments de CONTEXTE suivants pour répondre à la question finale. Veuille à suivre les règles suivantes :\n" +
        "1. Si tu trouves la réponse, rédige-la de manière semi-longue, en une dixaine de phrases maximum.\n" +
        "2. Tes seules connaissances sont le contexte donné. Si tu ne trouves pas la réponse UNIQUEMENT dans le CONTEXTE qui t'es donné, dis simplement : « Je n'arrive pas à trouver de réponse finale, car je n'ai pas connaissance de ce sujet. », et ne dis rien d'autre après.\n" +
        "3. Ce n'est pas grave si tu trouves pas la réponse."}
    
    messages = []
    messages.append(get_system_prompt())

    new_message = {
        "role": "user",
        "content": f"CONTEXTE:\n---\n{context}\n---\nQuestion: D'après le CONTEXTE UNIQUEMENT, {question}\n---\nRéponse utile:"
    }
    messages.append(new_message)
    if Config.DEBUG_PRINT: print(f"Messages: {messages}")

    # 4. appel LLM (Mistral 7B via DeepInfra)
    if Config.DEBUG_PRINT: print("Predicting response")
    answer = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=messages,
        max_tokens=Config.LLM_MAX_TOKENS,
        temperature=Config.LLM_TEMPERATURE,
        stream=False
    ).choices[0].message.content
    if Config.DEBUG_PRINT: print(f"Predicted response: {answer}")

    # 5. persiste la réponse/sauv en bdd
    msg = Message(chat_id=chat.chat_id, content=answer, is_user=False,
                  context=new_context)
    db.session.add(msg)
    db.session.commit()
    return msg
