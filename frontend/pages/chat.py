import streamlit as st
import requests

API_URL = "http://localhost:5000"

def list_chats():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{API_URL}/chats", headers=headers)

    if response.status_code == 200:
        chats = response.json()
        if chats:
            st.sidebar.subheader("Vos conversations")
            for chat in chats:
                if st.sidebar.button(key=chat['chat_id'], label=f"Conversation N°{chat['chat_id']}", type="tertiary", icon=":material/chat_bubble:"):
                    st.session_state["current_chat"] = chat['chat_id']
                    st.session_state["chat_history"] = []
        else:
            st.sidebar.info("Aucune conversation existante. Créez-en une nouvelle !")
    else:
        st.sidebar.error("Erreur lors de la récupération des conversations.")

def create_chat():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(f"{API_URL}/chats", json={"title": "Nouvelle conversation"}, headers=headers)

    if response.status_code == 201:
        st.success("Nouvelle conversation créée.")
        st.session_state["current_chat"] = response.json()["chat_id"]
        st.session_state["chat_history"] = []
    else:
        st.error("Erreur lors de la création de la conversation.")

def get_messages(chat_id):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{API_URL}/chats/{chat_id}/messages", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("Erreur lors de la récupération des messages.")
        return []

def send_message(chat_id, content, is_user):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(f"{API_URL}/chats/{chat_id}/messages", json={"content": content, "is_user": is_user}, headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        st.error("Erreur lors de l'envoi du message.")
        return None

def chat():
    list_chats()
    if st.sidebar.button("Créer", icon=":material/add:"):
        create_chat()
        st.rerun()
    if st.session_state["current_chat"]:
        st.markdown(f"# Conversation N°{st.session_state['current_chat']}")
        messages = get_messages(st.session_state["current_chat"])
        if messages:
            st.session_state["chat_history"] = messages
            # Display chat messages from history on app rerun
            for message in st.session_state.chat_history:
                role = "user" if message["is_user"] == True else "assistant"
                with st.chat_message(role):
                    st.markdown(message["content"])
        else:
            st.session_state["chat_history"] = []

        # Accept user input
        if prompt := st.chat_input("Posez votre question ici..."):
            # Display user message in chat message container
            with st.chat_message("user"):
                message_placeholder = st.empty()
                message_placeholder.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                response = send_message(st.session_state["current_chat"], prompt, is_user=True)
                full_response = response["content"]
                message_placeholder.markdown(full_response)