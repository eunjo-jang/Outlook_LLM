import os
import json
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from typing import List
from openai import OpenAI

# ==== STEP 1: Load ENV ====
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Available OpenAI models
AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4o-mini", 
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]

# ==== STEP 2: Load FAISS + Chunk Data ====
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_path = os.path.join(project_root, "data", "faiss_index.bin")
chunks_path = os.path.join(project_root, "data", "emails_chunked.jsonl")

index = faiss.read_index(index_path)

chunks = []
with open(chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        chunks.append(json.loads(line))

# ==== STEP 3: Load Embedding Model ====
model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L6-v2")

# ==== STEP 4: Search Function ====
def search_faiss(query: str, top_k: int = 5) -> List[str]:
    query_embedding = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)
    results = [chunks[i]["chunk"] for i in I[0]]
    return results

# ==== STEP 5: Prompt Creation ====
def build_prompt(context_chunks: List[str], user_question: str, chat_history: List[dict] = None) -> str:
    context = "\n---\n".join(context_chunks)
    
    # Build conversation history if provided
    history_text = ""
    if chat_history:
        history_text = "\n\nPrevious conversation:\n"
        for msg in chat_history[-6:]:  # Keep last 6 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
    
    return f"""
You are an assistant helping answer questions from email data. You can reference previous conversation context when relevant.

<context>
{context}
</context>
{history_text}

Question: {user_question}
Answer:
"""

# ==== STEP 6: Call LLM ====

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_openai(prompt: str, model: str = DEFAULT_MODEL) -> str:
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model} not available. Available models: {AVAILABLE_MODELS}")
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# ==== STEP 7: Run RAG ====
def run_rag(query: str, model: str = DEFAULT_MODEL, chat_history: List[dict] = None):
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model} not available. Available models: {AVAILABLE_MODELS}")
    
    top_chunks = search_faiss(query, top_k=5)
    prompt = build_prompt(top_chunks, query, chat_history)
    
    print(f"\n🤖 [{model}] Answering...\n")
    return ask_openai(prompt, model)

# ==== STEP 8: Chat Session Management ====
class ChatSession:
    def __init__(self):
        self.history = []
    
    def add_message(self, role: str, content: str):
        """Add a message to chat history"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    
    def get_history(self):
        """Get chat history"""
        return self.history
    
    def clear_history(self):
        """Clear chat history"""
        self.history = []
    
    def get_recent_history(self, count: int = 10):
        """Get recent chat history"""
        return self.history[-count:] if self.history else []




    