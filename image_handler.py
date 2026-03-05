import streamlit as st
import urllib.parse
import random
import requests
import time

def handle_image_generation(prompt, client):
    status_box = st.status("🎨 Albert is creating art...", expanded=True)
    
    # Simple prompt enhancement
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"4k art prompt for: '{prompt}'. Under 25 words."}]
        )
        art_prompt = enh_resp.choices[0].message.content
    except:
        art_prompt = prompt

    clean_art = urllib.parse.quote(art_prompt.strip())
    seed = random.randint(1, 999999)
    image_url = f"https://gen.pollinations.ai/prompt/{clean_art}?width=1024&height=1024&nologo=true&seed={seed}"

    image_ready = False
    for i in range(12):
        try:
            if requests.head(image_url, timeout=5).status_code == 200:
                image_ready = True
                break
        except: pass
        time.sleep(1)

    if image_ready:
        st.image(image_url, caption=f"Prompt: {art_prompt}")
        return f"I painted: *{art_prompt}*"
    else:
        st.image(f"https://gen.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={seed}")
        return "The detailed version failed, so I made a quick sketch!"