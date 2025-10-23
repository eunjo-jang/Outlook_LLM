# Streamlit web app for email RAG system with chat interface
import streamlit as st
from email_rag import run_rag, AVAILABLE_MODELS, ChatSession
import time

# Initialize session state
if "chat_session" not in st.session_state:
    st.session_state.chat_session = ChatSession()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page configuration
st.set_page_config(
    page_title="Outlook Email RAG Chatbot",
    page_icon="📬",
    layout="wide"
)

# Sidebar for model selection and controls
with st.sidebar:
    st.title("⚙️ Settings")
    
    model_choice = st.selectbox(
        "🤖 Select Model", 
        options=AVAILABLE_MODELS, 
        index=0,
        help="Choose the OpenAI model to use for responses"
    )
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History", help="Clear all chat messages"):
        st.session_state.chat_session.clear_history()
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Display chat statistics
    st.subheader("📊 Chat Statistics")
    st.metric("Total Messages", len(st.session_state.messages))
    st.metric("User Messages", len([m for m in st.session_state.messages if m["role"] == "user"]))
    st.metric("Assistant Messages", len([m for m in st.session_state.messages if m["role"] == "assistant"]))

# Main chat interface
st.title("📬 Outlook Email RAG Chatbot")
st.caption("Ask questions about your email data. The assistant will search through your emails and provide contextual answers.")

# Display chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your emails..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.chat_session.add_message("user", prompt)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching emails and generating response..."):
            try:
                # Get answer with chat history
                answer = run_rag(
                    prompt, 
                    model=model_choice, 
                    chat_history=st.session_state.chat_session.get_history()
                )
                
                # Add assistant response to session
                st.session_state.chat_session.add_message("assistant", answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Display the response
                st.markdown(answer)
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.caption("💡 Tip: You can ask follow-up questions and the assistant will remember the conversation context.")