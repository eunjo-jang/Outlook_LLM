import json
import os
import chromadb
from chromadb.utils import embedding_functions

# --- 설정 ---
JSONL_PATH = "/home/eunjo/Desktop/Outlook_LLM_v3/data/outlook_chunk_emailwise.jsonl"  # 전처리된 이메일 청크 데이터
CHROMA_DB_PATH = "/home/eunjo/Desktop/Outlook_LLM_v3/data/vectorstore/chroma_outlook"  # 벡터 DB 저장 경로
COLLECTION_NAME = "email_rag_collection"
BATCH_SIZE = 500  # 일괄 삽입 단위

# 임베딩 모델 설정 (BGE-M3: 고성능 다국어 임베딩, GPU 가속)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-m3",
    device="cuda"  # GPU 사용
)


def build_chroma_db():
    print(f"ChromaDB 클라이언트 연결 및 컬렉션 '{COLLECTION_NAME}' 초기화...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 기존 컬렉션 삭제 후 재생성
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}  # 코사인 유사도 사용
    )

    documents, metadatas, ids = [], [], []
    counter = 0

    print(f"🚀 JSONL 파일 '{JSONL_PATH}' 로딩 중...")
    with open(JSONL_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON 디코딩 오류: {e} - 건너뜀")
                continue

            doc_id = f"email_{counter}_{record['metadata']['message_id']}"
            meta = {
                "thread_id": record['metadata'].get('thread_id', 'N/A'),
                "date": record['metadata'].get('date'),
                "sender": record['metadata'].get('from', [''])[0],
                "recipients": ", ".join(record['metadata'].get('to', [])),
                "subject_preview": record['content'].split('\n')[0][:100] + "...",
            }

            documents.append(record['content'])
            metadatas.append(meta)
            ids.append(doc_id)
            counter += 1

            if len(documents) >= BATCH_SIZE:
                print(f"{counter}개 문서 인덱싱 중...")
                collection.add(documents=documents, metadatas=metadatas, ids=ids)
                documents, metadatas, ids = [], [], []

    if documents:
        print(f"마지막 {len(documents)}개 문서 인덱싱 중...")
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    total = collection.count()
    print(f"인덱싱 완료! 총 {total}개의 문서가 저장되었습니다.")


if __name__ == "__main__":
    build_chroma_db()