import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Albert", page_icon="🤖", layout="wide")

# --- 2. SECURE API LOADING ---
client = setup_client()

# --- 3. UI SETUP ---
st.title("🤖 I am Albert")
st.caption("2026 Edition: Vision • Research • Unstoppable Art")

with st.sidebar:
    st.header("Settings & Files")
    uploaded_file = st.file_uploader("Upload Image/PDF/Doc", type=["pdf", "docx", "jpg", "jpeg", "png"])
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("Draw me a neon city... or ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        img_triggers = ["draw", "generate", "image", "paint", "picture", "create"]

        if any(word in prompt.lower() for word in img_triggers):
            # --- PATH A: IMAGE GENERATION ---
            full_response = handle_image_generation(prompt, client)
        else:
            # --- PATH B: TEXT / VISION / RESEARCH ---
            full_response = handle_text_chat(prompt, client, uploaded_file, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": full_response})