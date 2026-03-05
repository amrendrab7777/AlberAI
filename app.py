import streamlit as st
import llm_logic
import tools
import artist

st.set_page_config(page_title="Albert 2026", layout="wide")
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Albert..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if any(w in prompt.lower() for w in ["draw", "paint", "generate"]):
            with st.spinner("🎨 Albert is painting..."):
                img = artist.create_art(prompt)
                if img:
                    st.image(img, caption=prompt)
                else: st.error("Failed to generate image.")
        else:
            response = llm_logic.query_ai([{"role": "user", "content": prompt}])
            st.write("Response generated via AI Brain.")

    st.session_state.messages.append({"role": "assistant", "content": "Done."})