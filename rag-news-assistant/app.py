import streamlit as st
from loader import load_news
from rag_pipeline import RAGPipeline

st.title("📰 News-Based Q&A Assistant (RAG)")

@st.cache_resource
def get_pipeline():
    docs = load_news()
    return RAGPipeline(docs)

pipeline = get_pipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a question about the news:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Retrieving answer..."):
        answer = pipeline.answer(user_input)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)