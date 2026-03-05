from PyPDF2 import PdfReader
from duckduckgo_search import DDGS

def extract_text(file):
    if file and file.type == "application/pdf":
        return "\n".join([page.extract_text() for page in PdfReader(file).pages])
    return ""

def web_search(query):
    with DDGS() as ddgs:
        return "\n".join([r['body'] for r in ddgs.text(query, max_results=2)])