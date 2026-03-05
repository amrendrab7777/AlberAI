import streamlit as st
import urllib.parse
import random
import requests
import time


def handle_image_generation(prompt, client):
    """
    PATH A: Handles all image generation requests.
    - Uses Groq LLM to enhance the user's prompt into a cinematic art description.
    - Builds a Pollinations.ai URL and validates it with a resilient retry loop.
    - Falls back to a simple quick-sketch URL if the server is too slow.
    Returns the assistant's final text response string.
    """
    status_box = st.status("🎨 Albert is creating art...", expanded=True)

    # Step 1: Expand the prompt using Groq (max 25 words)
    enhance_cmd = f"Rewrite as a 4k art prompt: '{prompt}'. Style: cinematic. UNDER 25 WORDS. No preamble."
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}]
        )
        art_prompt = enh_resp.choices[0].message.content
    except:
        art_prompt = prompt

    # Step 2: Build the Pollinations image URL
    clean_art = urllib.parse.quote(art_prompt.strip())
    seed = random.randint(1, 999999)
    image_url = (
        f"https://gen.pollinations.ai/prompt/{clean_art}"
        f"?width=1024&height=1024&nologo=true&seed={seed}&cache={time.time()}"
    )

    # Step 3: Resilient validation loop (12 retries, 1 second apart)
    image_ready = False
    for i in range(12):
        status_box.update(label=f"🖌️ Painting... ({i+1}/12s)", state="running")
        try:
            r = requests.head(image_url, timeout=5)
            if r.status_code == 200:
                image_ready = True
                break
        except:
            pass
        time.sleep(1)

    # Step 4: Display result or fallback
    if image_ready:
        status_box.update(label="✅ Masterpiece Complete!", state="complete")
        st.image(image_url, caption=f"Prompt: {art_prompt}")
        st.markdown(f"**[💾 Download High-Res]({image_url})**")
        full_response = f"I've painted that for you! Prompt used: *{art_prompt}*"
    else:
        # Emergency fallback with the original simple prompt
        status_box.update(label="⚠️ Server Busy - Using Quick Mode", state="running")
        fallback_url = f"https://gen.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?seed={seed}"
        st.image(fallback_url, caption="Albert's Quick Sketch")
        status_box.update(label="✅ Quick Sketch Complete", state="complete")
        full_response = "The detailed version timed out, so I made a quick sketch for you!"

    return full_response