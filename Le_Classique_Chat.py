import ollama
import streamlit as st
import warnings

warnings.filterwarnings("ignore")

st.title("Mon Chat de Le Chat")
st.caption("Un Chatbot à partir de Llama3.2")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "En quoi puis-je vous aider?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Modèle en local avec ollama
    stream = ollama.chat(
        model='llama3.2',
        messages=st.session_state.messages,
        stream=True
    )

    full_response = ""
    response_placeholder = st.empty()

    for chunk in stream:
        content = chunk['message']['content']
        full_response += content
        # Mettre à jour l'affichage en temps réel
        response_placeholder.chat_message("assistant").write(full_response)

    # Ajouter la réponse complète à l'état de la session après avoir reçu tous les morceaux
    st.session_state.messages.append({"role": "assistant", "content": full_response})
