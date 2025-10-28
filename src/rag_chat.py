from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY is not set. Please add it to your .env or export it.")
os.environ["OPENAI_API_KEY"] = api_key

# ===== 2️⃣ 임베딩 모델 및 DB 로딩 =====
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cuda"}  # GPU 사용
)

vectorstore = Chroma(
    persist_directory="../vectorstore/chroma_outlook",  # 벡터 DB 경로
    embedding_function=embedding_model
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# ===== 3️⃣ 프롬프트 정의 =====
prompt_template = """
You are an expert assistant for analyzing Outlook email data.

When answering a question, follow these guidelines:

1. If the question is about a mail thread: summarize the flow of the thread in chronological order. Clarify who said what, to whom, and what actions or replies were requested or made.

2. If the question is a conceptual one: provide a general answer based on common knowledge, then enrich the response with any relevant content from the documents.

3. Filter or summarize the information as needed. Focus on delivering the most relevant and concise insight.

Question: {question}

Reference documents:
{context}
"""

rag_prompt = ChatPromptTemplate.from_template(prompt_template)

# ===== 4️⃣ LLM + 체인 연결 =====
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# Chain 구성: context → prompt → LLM
rag_chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | rag_prompt
    | llm
)

# ===== 5️⃣ 실행 예시 =====
if __name__ == "__main__":
    while True:
        query = input("\n📝 질문을 입력하세요 (종료하려면 'exit'): ")
        if query.strip().lower() == "exit":
            break

        result = rag_chain.invoke(query)
        print(f"\n📘 답변:\n{result.content}")