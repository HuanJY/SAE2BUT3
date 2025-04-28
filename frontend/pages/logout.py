import streamlit as st

def logout():
    if st.button("Log out"):
        st.session_state["token"] = None
        st.session_state["chat_history"] = []
        st.session_state["current_chat"] = None
        st.rerun()