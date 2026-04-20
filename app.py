import streamlit as st
from config import setup_client
from image_handler import handle_image_generation
from chat_handler import handle_text_chat

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Albert", page_icon="🤖", layout="wide")

# --- 2. MOBILE FIX: Disable Pull to Refresh ---
st.markdown("""
    <style>
        * { overscroll-behavior-y: none !important; }
        html, body { overscroll-behavior-y: none !important; }
        .main, .block-container { overscroll-behavior-y: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SECURE API LOADING ---
client = setup_client()

# --- 4. UI SETUP ---
st.title("🤖 I am Albert the AI assistant")
st.caption("2026 Edition: Vision • Research • Unstoppable Art")

with st.sidebar:
    st.header("Settings & Files")
    uploaded_file = st.file_uploader("Upload Image/PDF/Doc", type=["pdf", "docx", "jpg", "jpeg", "png"])
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Render chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str) and msg["content"].startswith("__IMAGE__"):
            image_url = msg["content"].replace("__IMAGE__", "")
            st.markdown(
                f'<img src="{image_url}" width="100%" style="border-radius: 12px;" />',
                unsafe_allow_html=True
            )
        else:
            st.markdown(msg["content"])

# --- 5. CHAT LOGIC ---
if prompt := st.chat_input("Draw me a neon city... or ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # FIX: Stricter multi-word triggers to avoid false positives on
        # normal questions containing "image", "picture", "create", etc.
        img_triggers = [
            "draw me", "draw a", "draw an",
            "generate an image", "generate a picture", "generate art",
            "paint me", "paint a", "paint an",
            "create an image", "create a picture", "create art",
            "make an image", "make a picture", "make art",
            "show me a picture", "show me an image",
        ]

        prompt_lower = prompt.lower()
        is_image_request = any(trigger in prompt_lower for trigger in img_triggers)

        if is_image_request:
            # --- PATH A: IMAGE GENERATION ---
            full_response = handle_image_generation(prompt, client)
        else:
            # --- PATH B: TEXT / VISION / RESEARCH ---
            full_response = handle_text_chat(prompt, client, uploaded_file, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": full_response})