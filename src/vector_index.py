import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ===== 1️⃣ Load Model =====
model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
model = SentenceTransformer(model_name)
print(f"✅ Loaded embedding model: {model_name}")

# ===== 2️⃣ Read JSONL =====
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jsonl_path = os.path.join(project_root, "data", "emails_chunked.jsonl")
chunks = []

with open(jsonl_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            chunks.append(json.loads(line))
        except json.JSONDecodeError:
            continue

print(f"✅ Loaded {len(chunks)} chunks from {jsonl_path}")

# ===== 3️⃣ Extract Text Only =====
texts = [c["chunk"] for c in chunks if c.get("chunk")]

# ===== 4️⃣ Generate Embeddings =====
print("🔍 Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, device="cuda")

# ===== 5️⃣ Create FAISS Index =====
d = embeddings.shape[1]  # Vector dimension (usually 384)
index = faiss.IndexFlatL2(d)

# Move to GPU if available
if faiss.get_num_gpus() > 0:
    print("⚡ Using GPU for FAISS indexing")
    res = faiss.StandardGpuResources()
    index = faiss.index_cpu_to_gpu(res, 0, index)

# Add vectors
index.add(embeddings)
print(f"✅ Indexed {index.ntotal} chunks")

# ===== 6️⃣ Save Index =====
index_path = os.path.join(project_root, "data", "faiss_index.bin")
faiss.write_index(index, index_path)
print(f"💾 FAISS index saved: {index_path}")