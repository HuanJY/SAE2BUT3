import streamlit as st
import requests

API_URL = "http://localhost:5000"

def register():
    st.markdown("# Inscription")
    st.sidebar.header("Inscription")

    firstname = st.text_input("Prénom")
    lastname = st.text_input("Nom")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("S'inscrire"):
        response = requests.post(f"{API_URL}/register", json={
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password": password
        })
        if response.status_code == 201:
            st.success("Inscription réussie, connecte-toi maintenant !")
        else:
            st.error(response.json().get("error", "Erreur lors de l'inscription"))