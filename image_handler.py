import streamlit as st
import urllib.parse
import random


def handle_image_generation(prompt, client):
    status_box = st.status("🎨 Albert is creating art...", expanded=True)

    # Step 1: Enhance prompt with Groq
    enhance_cmd = (
        f"Rewrite as a vivid 4k art prompt: '{prompt}'. "
        f"Style: cinematic. UNDER 20 WORDS. Only the prompt, no preamble."
    )
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}]
        )
        art_prompt = enh_resp.choices[0].message.content.strip()
    except Exception:
        art_prompt = prompt

    # Step 2: Build Pollinations URL
    seed = random.randint(1, 999999)
    encoded_prompt = urllib.parse.quote(art_prompt, safe="")
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
    )

    # Step 3: Render image directly in the BROWSER via <img> tag
    # This completely bypasses Cloudflare's server-side block (Status 530)
    # because the user's browser fetches it, not Streamlit's server.
    status_box.update(label="✅ Sending to your browser...", state="complete")

    st.markdown(
        f"""
        <img src="{image_url}" 
             width="100%" 
             style="border-radius: 12px; margin-top: 8px;"
             alt="Generated image: {art_prompt}" />
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"📝 **Prompt:** *{art_prompt}*")
    st.markdown(f"**[💾 Download High-Res]({image_url})**")

    full_response = f"I've painted that for you! Prompt used: *{art_prompt}*"
    return full_response