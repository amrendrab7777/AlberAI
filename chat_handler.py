import streamlit as st
from utils import extract_text, encode_image, get_web_context


def handle_text_chat(prompt, client, uploaded_file, messages):
    """
    PATH B: Handles all text, vision, and research-based chat requests.
    - Detects whether the uploaded file is an image or a document.
    - Fetches live web context via DuckDuckGo.
    - Selects the appropriate Groq model (vision vs text).
    - Streams the response token-by-token into the Streamlit UI.
    Returns the assistant's final complete response string.
    """
    file_txt, is_img, b64_img = "", False, None

    # Step 1: Process any uploaded file
    if uploaded_file:
        if uploaded_file.type.startswith("image"):
            is_img = True
            b64_img = encode_image(uploaded_file)
        else:
            file_txt = extract_text(uploaded_file)

    # Step 2: Fetch web context for the query
    with st.status("🔍 Researching...", expanded=False):
        web_info = get_web_context(prompt)

    # Step 3: Build conversation history (exclude the latest user message,
    # since we're constructing it manually below with file/web context)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[:-1]
    ]

    # Step 4: Build the final user message and pick the right model
    if is_img:
        history.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Context: {web_info}\n\nQ: {prompt}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
            ]
        })
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
    else:
        history.append({
            "role": "user",
            "content": f"File: {file_txt}\nWeb: {web_info}\nQ: {prompt}"
        })
        model = "llama-3.3-70b-versatile"

    # Step 5: Stream the response
    resp_placeholder = st.empty()
    full_response = ""
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=history,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                resp_placeholder.markdown(full_response + "▌")
        resp_placeholder.markdown(full_response)
    except Exception as e:
        st.error(f"Error: {str(e)}")

    return full_response