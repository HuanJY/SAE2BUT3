import streamlit as st
import requests

API_URL = "http://localhost:5000"

def login():
    st.markdown("# Connexion")
    st.sidebar.header("Connexion")

    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        response = requests.post(f"{API_URL}/login", json={
            "email": email,
            "password": password
        })

        if response.status_code == 200:
            st.session_state["token"] = response.json()["token"]
            st.success("Connexion réussie ✅")
            st.rerun()
        else:
            st.error(response.json().get("error", "Identifiants invalides"))