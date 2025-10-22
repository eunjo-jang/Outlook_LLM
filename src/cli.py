# CLI interface for email RAG system
from email_rag import run_rag, AVAILABLE_MODELS

if __name__ == "__main__":
    print("🤖 Available models:")
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
    
    user_query = input("\n❓ Enter your question: ")
    answer = run_rag(user_query, model=selected_model)
    print("\n📝 Answer:\n", answer)