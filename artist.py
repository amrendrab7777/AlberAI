import requests
import urllib.parse

def create_art(prompt):
    clean_p = urllib.parse.quote(prompt)
    url = f"https://gen.pollinations.ai/prompt/{clean_p}?model=flux&width=1024&height=1024&nologo=true"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)
    return response.content if response.status_code == 200 else None