import streamlit as st

def home():
    st.markdown("# Accueil")
    st.markdown("### Bienvenue sur **EcoChatBot**")
    
    st.write("""
    ÉcoBot est votre assistant spécialisé en **économie**.
    
    Grâce à cette application, vous pouvez :
    - Poser des questions sur des concepts économiques (inflation, PIB, marché, etc.)
    - Discuter de l’actualité économique
    - Obtenir des explications claires sur les politiques monétaires, fiscales et autres
    - Approfondir vos connaissances pour vos études, votre veille ou votre curiosité personnelle

    ### Pour commencer :
    - Cliquez sur **Connexion** si vous avez déjà un compte
    - Cliquez sur **Inscription** pour créer un nouveau compte
    - Une fois connecté, créez une nouvelle conversation ou ouvrez-en une existante.

    ---
    *Notre application utilise l’IA pour vous aider à mieux comprendre le monde économique. Posez vos questions, et laissez-vous surprendre.*
    """)
