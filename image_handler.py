import streamlit as st
import urllib.parse
import hashlib


def handle_image_generation(prompt, client):
    status_box = st.status("🎨 Albert is creating art...", expanded=True)

    # --- Step 1: Enhance the prompt with Groq ---
    # temperature=0 ensures the same rewritten prompt for the same input,
    # which in turn produces a consistent seed and a consistent image.
    enhance_cmd = (
        f"Rewrite as a vivid 4k art prompt for exactly this subject: '{prompt}'. "
        f"Style: cinematic, photorealistic. UNDER 20 WORDS. "
        f"Only the prompt, no preamble, no extra text, no quotes."
    )
    try:
        enh_resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": enhance_cmd}],
            temperature=0,
            max_tokens=60  # FIX: Prompt rewrite needs at most ~20 words; cap it tight
        )
        art_prompt = enh_resp.choices[0].message.content.strip()
        # Safety fallback: if the model returns an empty string, use original
        if not art_prompt:
            art_prompt = prompt
    except Exception as e:
        st.warning(f"Prompt enhancement failed ({e}), using original prompt.")
        art_prompt = prompt

    # --- Step 2: Generate a FIXED seed from the enhanced prompt ---
    # Same prompt → same seed → same image every time (deterministic output)
    seed = int(hashlib.md5(art_prompt.lower().encode()).hexdigest(), 16) % 999999

    # --- Step 3: Build the Pollinations URL ---
    encoded_prompt = urllib.parse.quote(art_prompt, safe="")
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024&height=1024&nologo=true&enhance=false&seed={seed}&model=flux"
    )

    # --- Step 4: Render image ---
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

    st.markdown(f"📝 **Prompt used:** *{art_prompt}*")
    st.markdown(f"**[💾 Download High-Res]({image_url})**")

    # Prefix with __IMAGE__ so the history renderer knows to show <img> not text
    return f"__IMAGE__{image_url}"