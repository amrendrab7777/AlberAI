import groq
import streamlit as st

def get_client():
    return groq.Groq(api_key=st.secrets["GROQ_API_KEY"])

def query_ai(messages, model="llama-3.3-70b-versatile"):
    client = get_client()
    return client.chat.completions.create(model=model, messages=messages, stream=True)