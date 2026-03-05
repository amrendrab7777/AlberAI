import base64
import io
import docx  # Added missing import
from PIL import Image
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader

def extract_text(uploaded_file):
    text = ""
    # Check if uploaded_file is valid before accessing .type
    if uploaded_file and hasattr(uploaded_file, 'type'):
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        elif "officedocument.wordprocessingml.document" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
    return text

def encode_image(uploaded_file):
    img = Image.open(uploaded_file)
    img.thumbnail((1024, 1024))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_web_context(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results)
    except:
        return ""