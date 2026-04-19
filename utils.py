import base64
import io
import docx
from PIL import Image
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader

# FIX: Reject files larger than 10 MB before attempting to process them
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def extract_text(uploaded_file):
    """Extract plain text from a PDF or DOCX uploaded file."""
    text = ""

    if not uploaded_file or not hasattr(uploaded_file, "type"):
        return text

    # FIX: Guard against oversized files
    uploaded_file.seek(0, 2)  # Seek to end
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)     # Reset to start
    if file_size > MAX_FILE_SIZE_BYTES:
        import streamlit as st
        st.warning(f"⚠️ File is too large ({file_size // (1024*1024)} MB). "
                   f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB.")
        return text

    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        elif "officedocument.wordprocessingml.document" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        import streamlit as st
        st.warning(f"⚠️ Could not read file: {e}")

    return text


def encode_image(uploaded_file):
    """Resize and base64-encode an uploaded image for API submission."""
    # FIX: Guard against oversized images
    uploaded_file.seek(0, 2)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)
    if file_size > MAX_FILE_SIZE_BYTES:
        import streamlit as st
        st.warning(f"⚠️ Image is too large ({file_size // (1024*1024)} MB). "
                   f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB.")
        return None

    try:
        img = Image.open(uploaded_file)
        img.thumbnail((1024, 1024))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        import streamlit as st
        st.warning(f"⚠️ Could not process image: {e}")
        return None


def get_web_context(query):
    """Fetch a brief web summary for the given query using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results)
    except Exception as e:
        # FIX: Surface the error so it's visible during debugging,
        # instead of silently swallowing it with a bare `except`
        import streamlit as st
        st.warning(f"⚠️ Web search unavailable: {e}")
        return ""