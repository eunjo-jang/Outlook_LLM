import json
from pathlib import Path
from tqdm import tqdm

input_path = Path("/home/eunjo/Desktop/Outlook_LLM_v3/data/outlook_clean.jsonl")
output_path = Path("/home/eunjo/Desktop/Outlook_LLM_v3/data/outlook_chunk_emailwise.jsonl")

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def chunk_emailwise(emails):
    chunks = []
    for email in tqdm(emails, desc="Chunking emails"):
        chunk = {
            "content": f"{email.get('subject', '')}\n\n{email.get('body', '')}",
            "metadata": {
                "from": email["from_list"],
                "to": email["to_list"],
                "date": email["date_iso"],
                "message_id": email["message_id"],
                "in_reply_to": email.get("in_reply_to"),
                "references": email.get("references"),
                "thread_id": email.get("thread_id"),
                "attachments": email.get("attachments"),
                "name_email_map": email.get("name_email_map"),
            }
        }
        chunks.append(chunk)
    return chunks

# 실행
emails = load_jsonl(input_path)
chunks = chunk_emailwise(emails)
save_jsonl(output_path, chunks)
print(f"{len(chunks)}개 청크가 '{output_path}'로 저장되었습니다.")