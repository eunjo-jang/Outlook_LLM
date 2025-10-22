import json
import nltk
import os

# Download NLTK data (run once)
nltk.download('punkt')

from nltk.tokenize import sent_tokenize

# === Configuration ===
MAX_CHUNK_SIZE = 1000     # Maximum chunk length (character count)
OVERLAP_SIZE = 200        # Overlap size between chunks

def chunk_email_body(text, max_chunk_size=MAX_CHUNK_SIZE, overlap=OVERLAP_SIZE):
    """Split email body into sentences and chunk by maximum length"""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            # Apply overlap
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + " " + sentence
            else:
                current_chunk = sentence
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks


# === Example: JSONL file chunking ===
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_file = os.path.join(project_root, "data", "outlook_2021_cleaned.jsonl")
output_file = os.path.join(project_root, "data", "emails_chunked.jsonl")

with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "w", encoding="utf-8") as f_out:
    for line in f_in:
        try:
            email = json.loads(line)
            body = email.get("body", "")
            chunks = chunk_email_body(body)
            for idx, chunk in enumerate(chunks):
                chunked_email = {
                    "subject": email.get("subject", ""),
                    "from": email.get("from", ""),
                    "to": email.get("to", ""),
                    "date": email.get("date", ""),
                    "chunk_id": idx,
                    "chunk": chunk
                }
                f_out.write(json.dumps(chunked_email) + "\n")
        except json.JSONDecodeError:
            continue