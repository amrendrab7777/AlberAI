import streamlit as st
import urllib.parse
import random
import requests
import time
import io


def fetch_image_bytes(url, timeout=60):
    """
    Attempts a GET request to download image bytes from the given URL.
    Pollinations generates the image server-side, so we wait up to `timeout` seconds.
    Returns raw bytes on success, or None on failure.
    """
    try:
        r = requests.get(url, timeout=timeout)
        content_type = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in content_type:
            return r.content
    except Exception:
        pass
    return None


def handle_image_generation(prompt, client):
    """
    PATH A: Handles all image generation requests.
    - Uses Groq LLM to enhance the user's prompt into a cinematic art description.
    - Downloads the image bytes directly via GET (fixes broken-icon bug).
    - Falls back to the raw prompt if the enhanced version fails.
    Returns the assistant's final text response string.
    """
    status_box = st.status("🎨 Albert is creating art...", expanded=True)

    # Step 1: Expand the prompt using Groq (max 25 words)
    enhance_cmd = (
        f"Rewrite as a 4k art prompt: '{prompt}'. "
        f"Style: cinematic. UNDER 25 WORDS. No preamble."
    )
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}]
        )
        art_prompt = enh_resp.choices[0].message.content.strip()
    except Exception:
        art_prompt = prompt

    # Step 2: Build the Pollinations image URL
    seed = random.randint(1, 999999)
    image_url = (
        f"https://image.pollinations.ai/prompt/{urllib.parse.quote(art_prompt)}"
        f"?width=1024&height=1024&nologo=true&seed={seed}"
    )

    # Step 3: Download the image bytes directly (Pollinations blocks until ready)
    # KEY FIX: GET waits for generation to complete; HEAD does not.
    status_box.update(label="🖌️ Painting your image... (this may take ~15s)", state="running")
    image_bytes = fetch_image_bytes(image_url, timeout=60)

    # Step 4: Display result or fallback
    if image_bytes:
        status_box.update(label="✅ Masterpiece Complete!", state="complete")
        st.image(io.BytesIO(image_bytes), caption=f"Prompt: {art_prompt}")
        st.markdown(f"**[💾 Download High-Res]({image_url})**")
        full_response = f"I've painted that for you! Prompt used: *{art_prompt}*"
    else:
        # Fallback: try with the original raw prompt
        status_box.update(label="⚠️ Retrying with simple prompt...", state="running")
        fallback_url = (
            f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
            f"?seed={seed}"
        )
        fallback_bytes = fetch_image_bytes(fallback_url, timeout=30)

        if fallback_bytes:
            st.image(io.BytesIO(fallback_bytes), caption="Albert's Quick Sketch")
            status_box.update(label="✅ Quick Sketch Complete", state="complete")
            full_response = "The detailed version timed out, so here's a quick sketch!"
        else:
            status_box.update(label="❌ Image generation failed", state="error")
            full_response = "Sorry, image generation is unavailable right now. Please try again in a moment."

    return full_response