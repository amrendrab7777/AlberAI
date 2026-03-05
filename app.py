import streamlit as st
import groq
import base64
import io
import urllib.parse
import random
import requests
import time
from PIL import Image
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader
import docx

# --- 1. CONFIG & API ---
st.set_page_config(page_title="Albert", page_icon="🤖", layout="wide")

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = groq.Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ Add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 2. UTILITIES ---
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages: text += page.extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text

def encode_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((1024, 1024))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# --- 3. UI ---
st.title("🤖 Albert AI")
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("Draw a futuristic city..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # IMAGE GENERATION PATH
        if any(word in prompt.lower() for word in ["draw", "paint", "generate", "image", "create"]):
            status = st.status("🎨 Albert is painting...", expanded=True)
            
            # Use Llama to keep prompt clean and under 25 words
            try:
                enh = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Briefly describe this for AI art: '{prompt}'. Max 20 words."}]
                )
                art_prompt = enh.choices[0].message.content
            except: art_prompt = prompt

            # 2026 SECURE URL (Requires model + seed + headers)
            seed = random.randint(0, 999999)
            clean_p = urllib.parse.quote(art_prompt)
            # We add 'model=flux' because it's the most stable in 2026
            image_url = f"https://gen.pollinations.ai/prompt/{clean_p}?model=flux&width=1024&height=1024&seed={seed}&nologo=true"
            
            # FETCH IMAGE BYTES (Fixes the broken icon issue)
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(image_url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    status.update(label="✅ Masterpiece Complete!", state="complete")
                    # We display the raw bytes so Streamlit doesn't have to fetch the URL again
                    st.image(response.content, caption=f"Prompt: {art_prompt}")
                    st.markdown(f"[📥 Download]({image_url})")
                    full_resp = f"I've finished the painting: *{art_prompt}*"
                else:
                    status.update(label="❌ Server Error", state="error")
                    st.error(f"Server said: {response.status_code}. Try again in a minute.")
                    full_resp = "The art studio is closed for a moment. Try again?"
            except:
                st.error("Connection timed out.")
                full_resp = "I couldn't reach the art server."

        # TEXT/VISION PATH
        else:
            # ... (Existing Text Logic) ...
            resp_placeholder = st.empty()
            full_resp = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_resp += chunk.choices[0].delta.content
                    resp_placeholder.markdown(full_resp + "▌")
            resp_placeholder.markdown(full_resp)

    st.session_