# Streamlit web app for email RAG system
import streamlit as st
from email_rag import run_rag, AVAILABLE_MODELS

st.title("📬 Outlook Email RAG Chatbot")

query = st.text_input("❓ Enter your question")
model_choice = st.selectbox("🤖 Select model", options=AVAILABLE_MODELS, index=0)

if st.button("Ask Question") and query:
    with st.spinner("Generating answer..."):
        answer = run_rag(query, model=model_choice)
    
    st.subheader("🧠 Answer")
    st.markdown(answer)