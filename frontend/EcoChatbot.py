import streamlit as st
from pages.home import home
from pages.chat import chat
from pages.logout import logout
from pages.login import login
from pages.register import register

# Initialiser l'état de session
if "token" not in st.session_state:
    st.session_state["token"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = None

home_page = st.Page(home, title="Accueil", icon=":material/home:", default=True)
login_page = st.Page(login, title="Connexion", url_path="/login", icon=":material/login:")
register_page = st.Page(register, title="Inscription", url_path="/register", icon=":material/assignment_ind:")
logout_page = st.Page(logout, title="Déconnexion", url_path="/logout", icon=":material/logout:")

chat_page = st.Page(chat, title="Conversations", url_path="/chat", icon=":material/dashboard:")

if st.session_state["token"]:
    pg = st.navigation([home_page, chat_page, logout_page])
else:
    pg = st.navigation([home_page, login_page, register_page])
pg.run()