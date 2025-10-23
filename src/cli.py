# CLI interface for email RAG system with chat history
from email_rag import run_rag, AVAILABLE_MODELS, ChatSession

def print_chat_history(session: ChatSession, limit: int = 5):
    """Print recent chat history"""
    history = session.get_recent_history(limit)
    if not history:
        return
    
    print("\n" + "="*50)
    print("📜 Recent Chat History:")
    print("="*50)
    
    for msg in history:
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        role_name = "You" if msg["role"] == "user" else "Assistant"
        print(f"{role_icon} {role_name}: {msg['content']}")
    
    print("="*50)

def main():
    print("🤖 Outlook Email RAG Chatbot")
    print("="*40)
    
    # Model selection
    print("\nAvailable models:")
    for i, model in enumerate(AVAILABLE_MODELS, 1):
        print(f"  {i}. {model}")
    
    try:
        model_choice = input(f"\nSelect a model (1-{len(AVAILABLE_MODELS)}, default: 1): ").strip()
        if not model_choice:
            selected_model = AVAILABLE_MODELS[0]
        else:
            model_index = int(model_choice) - 1
            selected_model = AVAILABLE_MODELS[model_index]
    except (ValueError, IndexError):
        print("Invalid selection. Using default model.")
        selected_model = AVAILABLE_MODELS[0]
    
    print(f"\n✅ Using model: {selected_model}")
    print("\n💡 Commands:")
    print("  - Type your question and press Enter")
    print("  - Type 'history' to see chat history")
    print("  - Type 'clear' to clear chat history")
    print("  - Type 'quit' or 'exit' to exit")
    print("  - Type 'help' to see this help")
    
    # Initialize chat session
    session = ChatSession()
    
    while True:
        print("\n" + "-"*40)
        user_input = input("❓ You: ").strip()
        
        if not user_input:
            continue
            
        # Handle special commands
        if user_input.lower() in ['quit', 'exit']:
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'history':
            print_chat_history(session)
            continue
        elif user_input.lower() == 'clear':
            session.clear_history()
            print("🗑️ Chat history cleared!")
            continue
        elif user_input.lower() == 'help':
            print("\n💡 Commands:")
            print("  - Type your question and press Enter")
            print("  - Type 'history' to see chat history")
            print("  - Type 'clear' to clear chat history")
            print("  - Type 'quit' or 'exit' to exit")
            print("  - Type 'help' to see this help")
            continue
        
        # Add user message to history
        session.add_message("user", user_input)
        
        try:
            # Get answer with chat history
            answer = run_rag(user_input, model=selected_model, chat_history=session.get_history())
            
            # Add assistant response to history
            session.add_message("assistant", answer)
            
            print(f"\n🤖 Assistant: {answer}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or check your configuration.")

if __name__ == "__main__":
    main()