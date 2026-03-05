import base64
import io
from PIL import Image
from duckduckgo_search import DDGS
from PyPDF2 import PdfReader
import docx


def extract_text(uploaded_file):
    """
    Extracts text content from an uploaded PDF or DOCX file.
    Returns a plain string of the extracted text.
    """
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
    """
    Opens an uploaded image, resizes it to fit within 1024x1024,
    converts it to JPEG, and returns it as a base64-encoded string.
    """
    img = Image.open(uploaded_file)
    img.thumbnail((1024, 1024))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def get_web_context(query):
    """
    Performs a DuckDuckGo search for the given query and returns
    the top 2 result bodies joined as a single string.
    Returns an empty string on failure.
    """
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=2)]
            return "\n".join(results)
    except:
        return ""