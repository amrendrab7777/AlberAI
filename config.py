import streamlit as st
import groq

def setup_client():
    """
    Loads the Groq API key from Streamlit Secrets and returns an authenticated client.
    Stops the app if the key is missing.
    """
    try:
        API_KEY = st.secrets["GROQ_API_KEY"]
        client = groq.Groq(api_key=API_KEY)
        return client
    except Exception:
        st.error("⚠️ Setup Error: Add your 'GROQ_API_KEY' to Streamlit Secrets.")
        st.stop()