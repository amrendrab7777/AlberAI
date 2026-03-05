import streamlit as st
import groq
import base64
import io
import urllib.parse
import random
from PIL import Image
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader
import docx

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Albert", page_icon="🤖", layout="centered")

# --- 2. SECURE API LOADING ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = groq.Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ Developer Setup Required: Add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

# --- 3. UTILITY FUNCTIONS ---
def extract_text(uploaded_file):
    """Reads text from PDF and DOCX files."""
    text = ""
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    return text

def encode_image(uploaded_file):
    """Resizes and compresses image to avoid 'Request Entity Too Large' errors."""
    img = Image.open(uploaded_file)
    img.thumbnail((1024, 1024)) # Resize to max 1024px
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_web_context(query):
    """Fetches real-time context from the web."""
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results)
    except:
        return ""

# --- 4. ALBERT UI ---
st.title("🤖 I am Albert")
st.caption("Memory-Enabled AI with Vision, Research, and Art Skills")

# Sidebar
with st.sidebar:
    st.header("📁 Upload Files")
    uploaded_file = st.file_uploader("Upload Image, PDF, or Doc", type=["pdf", "docx", "jpg", "jpeg", "png"])
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. CHAT LOGIC ---
if prompt := st.chat_input("Ask Albert to draw, analyze a file, or search..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # --- PATH A: IMAGE GENERATION (Pollinations + Auto-Enhance) ---
        image_keywords = ["draw", "generate", "image", "paint", "create a picture"]
        if any(word in prompt.lower() for word in image_keywords):
            with st.spinner("🎨 Albert is brainstorming an artistic masterpiece..."):
                # Use Llama to enhance the prompt
                enhance_instruction = f"Transform this image request into a highly detailed, 4k AI art prompt: '{prompt}'. Respond ONLY with the new prompt."
                try:
                    enhanced_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": enhance_instruction}]
                    )
                    art_prompt = enhanced_resp.choices[0].message.content
                except:
                    art_prompt = prompt

                encoded_art = urllib.parse.quote(art_prompt.strip())
                seed = random.randint(1, 100000)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_art}?width=1024&height=1024&nologo=true&seed={seed}"
                
                st.image(image_url, caption="Albert's Enhanced Creation")
                with st.expander("Show Art Details"):
                    st.write(f"**Enhanced Prompt:** {art_prompt}")
                
                full_response = f"I've painted that for you! ![Image]({image_url})"

        # --- PATH B: TEXT & VISION (Groq + Memory) ---
        else:
            file_context = ""
            is_image = False
            base64_image = None
            
            if uploaded_file:
                if uploaded_file.type.startswith("image"):
                    is_image = True
                    with st.spinner("Optimizing image..."):
                        base64_image = encode_image(uploaded_file)
                else:
                    with st.spinner("Reading document..."):
                        file_context = extract_text(uploaded_file)

            with st.status("🔍 Researching...", expanded=False):
                web_info = get_web_context(prompt)
            
            # Construct Memory
            messages_to_send = []
            for m in st.session_state.messages[:-1]:
                messages_to_send.append({"role": m["role"], "content": m["content"]})
            
            if is_image and base64_image:
                messages_to_send.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Context: {web_info}\n\nQuestion: {prompt}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                })
            else:
                combined_prompt = f"File Context: {file_context}\nWeb Info: {web_info}\nUser Question: {prompt}"
                messages_to_send.append({"role": "user", "content": combined_prompt})

            response_placeholder = st.empty()
            full_response = ""

            try:
                model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct" if is_image else "llama-3.3-70b-versatile"
                stream = client.chat.completions.create(
                    model=model_to_use,
                    messages=messages_to_send,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Albert error: {str(e)}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})