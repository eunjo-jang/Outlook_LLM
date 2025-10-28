# rag_streamlit_chatbot.py
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.embeddings import HuggingFaceEmbeddings

# =====================
# 0. Load API key
# =====================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file or environment variable.")

# =====================
# 1. Streamlit UI Setup
# =====================
st.set_page_config(page_title="Outlook RAG Chatbot", layout="wide", initial_sidebar_state="collapsed")
st.title("📧 ITER Outlook RAG Chatbot")
st.caption("💬 Ask questions about ITER Vacuum Vessel project emails")

# 채팅 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "source_docs" not in st.session_state:
    st.session_state.source_docs = {}

# =====================
# 2. Load Vector DB
# =====================
CHROMA_PATH = "../data/vectorstore/chroma_outlook"
COLLECTION_NAME = "email_rag_collection"

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cuda"}  # GPU 사용 (RTX 6000 Ada)
)

vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 10})  # Top 10 유사 문서 검색

# =====================
# 3. Query Analysis & Filtering
# =====================
def extract_query_filters(query: str, llm) -> dict:
    """LLM으로 쿼리에서 필터 조건 추출"""
    filter_prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a query analyzer. Extract search filters from the user's question.\n"
         "Return ONLY a valid JSON object with these fields (use null if not found):\n"
         "{{\n"
         '  "date_exact": "YYYY-MM-DD" or null,\n'
         '  "date_month": "YYYY-MM" or null,\n'
         '  "date_year": "YYYY" or null,\n'
         '  "sender_name": "name" or null,\n'
         '  "keywords": ["keyword1", "keyword2"] or []\n'
         "}}\n\n"
         "Examples:\n"
         'Q: "What happened on January 31, 2021?" → {{"date_exact": "2021-01-31", ...}}\n'
         'Q: "Emails in July 2021" → {{"date_month": "2021-07", ...}}\n'
         'Q: "What did Alex Martin say?" → {{"sender_name": "Alex Martin", ...}}\n'
         'Q: "ANB reports" → {{"keywords": ["ANB", "report"], ...}}\n'),
        ("human", "Question: {question}\n\nReturn JSON only:")
    ])
    
    try:
        from langchain_core.output_parsers import JsonOutputParser
        parser = JsonOutputParser()
        chain = filter_prompt | llm | parser
        filters = chain.invoke({"question": query})
        return filters
    except:
        return {}

def filter_docs_by_metadata(docs, filters: dict):
    """추출된 필터로 문서 필터링"""
    if not filters:
        return docs
    
    filtered = docs
    
    # 정확한 날짜 매칭
    if filters.get("date_exact"):
        target_date = filters["date_exact"]
        filtered = [d for d in filtered if target_date in d.metadata.get("date", "")]
    
    # 월 범위 매칭 (e.g., 2021-07)
    elif filters.get("date_month"):
        target_month = filters["date_month"]
        filtered = [d for d in filtered if target_month in d.metadata.get("date", "")]
    
    # 연도 매칭
    elif filters.get("date_year"):
        target_year = filters["date_year"]
        filtered = [d for d in filtered if target_year in d.metadata.get("date", "")]
    
    # 발신자 매칭 (이름 또는 이메일)
    if filters.get("sender_name"):
        sender_name = filters["sender_name"].lower()
        filtered = [d for d in filtered 
                   if sender_name in d.metadata.get("sender", "").lower()]
    
    return filtered

# =====================
# 4. Document Formatting
# =====================
def format_docs(docs):
    """문서를 문자열로 포맷팅 - 메타데이터 강조로 날짜/발신자 기반 검색 정확도 향상"""
    formatted = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        sender = meta.get('sender', 'Unknown')
        recipients = meta.get('recipients', 'Unknown')
        date = meta.get('date', 'Unknown')
        attachments = meta.get('attachments', [])
        content = doc.page_content
        
        # 첨부파일 포맷팅
        attachments_str = ', '.join(attachments) if attachments else 'None'
        
        formatted.append(
            f"========== EMAIL {i} ==========\n"
            f"📅 DATE: {date}\n"
            f"👤 FROM: {sender}\n"
            f"👥 TO: {recipients}\n"
            f"📎 ATTACHMENTS: {attachments_str}\n"
            f"📧 CONTENT:\n{content}\n"
            f"================================"
        )
    return "\n\n".join(formatted)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant specialized in ITER project email communications.\n"
     "You have access to email archives from the ITER Vacuum Vessel project.\n\n"
     "IMPORTANT INSTRUCTIONS:\n"
     "1. Use the provided email context to answer questions about:\n"
     "   - VV (Vacuum Vessel) components and procedures\n"
     "   - Transportation and logistics\n"
     "   - ANB reports and inspections\n"
     "   - Meeting schedules and discussions\n"
     "   - Technical documentation\n\n"
     "2. If the context contains relevant information, cite it in your answer.\n"
     "3. For conceptual questions about ITER/fusion, combine the email context with your knowledge.\n"
     "4. If no relevant emails are found, say so clearly.\n"
     "5. When discussing email threads, describe the conversation flow.\n"
     "6. Be specific about dates, people, and technical details when available.\n\n"
     "⚠️ CRITICAL FOR DATE/METADATA-BASED QUERIES:\n"
     "- Pay CLOSE ATTENTION to the 📅 DATE field in each email\n"
     "- When asked about specific dates, filter emails by matching the DATE exactly\n"
     "- Check 📎 ATTACHMENTS when asked about files or documents\n"
     "- Use 👤 FROM and 👥 TO fields for sender/recipient questions\n"
     "- List ALL matching emails when asked about a specific date or person\n"
     "- Format dates clearly (e.g., 'January 31, 2021' or '2021-01-31')\n"),
    ("human", "Question: {question}\n\nRelevant Emails:\n{context}")
])

# =====================
# 5. Smart Retrieval Function
# =====================
def smart_retrieve(query: str):
    """쿼리 분석 + 메타데이터 필터링(선행) + 의미 검색을 결합한 스마트 검색"""
    # 1단계: LLM으로 쿼리 분석
    filters = extract_query_filters(query, llm)
    
    # 2단계: ChromaDB where 절 구성 (메타데이터 필터링 선행)
    where_filter = None
    if filters and any(filters.values()):
        where_conditions = []
        
        # 날짜 필터링
        if filters.get("date_exact"):
            where_conditions.append({"date": {"$contains": filters["date_exact"]}})
        elif filters.get("date_month"):
            where_conditions.append({"date": {"$contains": filters["date_month"]}})
        elif filters.get("date_year"):
            where_conditions.append({"date": {"$contains": filters["date_year"]}})
        
        # 발신자 필터링
        if filters.get("sender_name"):
            where_conditions.append({"sender": {"$contains": filters["sender_name"]}})
        
        # 여러 조건이 있으면 AND 연산
        if len(where_conditions) > 1:
            where_filter = {"$and": where_conditions}
        elif len(where_conditions) == 1:
            where_filter = where_conditions[0]
    
    # 3단계: 메타데이터 필터링 후 유사도 검색 (k=10)
    try:
        if where_filter:
            # 메타데이터 필터링을 먼저 적용한 검색
            candidates = vectorstore.similarity_search(query, k=10, filter=where_filter)
        else:
            # 필터 없으면 일반 유사도 검색
            candidates = vectorstore.similarity_search(query, k=10)
    except Exception as e:
        # 필터링 실패시 폴백
        print(f"Filtered search failed: {e}, falling back to normal search")
        candidates = vectorstore.similarity_search(query, k=10)
    
    return candidates

# =====================
# 6. LLM and Chain
# =====================
llm = ChatOpenAI(model="gpt-4o", temperature=0)

rag_chain = (
    {
        "context": lambda x: format_docs(smart_retrieve(x)),
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

# =====================
# 5. Chat UI with History
# =====================

# 사이드바에 Clear Chat 버튼 추가
with st.sidebar:
    st.markdown("### 💬 Chat Controls")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.source_docs = {}
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Chat Statistics")
    st.metric("Total Messages", len(st.session_state.messages))
    st.metric("Q&A Pairs", len(st.session_state.messages) // 2)

# 채팅 메시지 히스토리 표시
chat_container = st.container()
with chat_container:
    # 첫 방문 시 환영 메시지 표시
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            st.markdown("""
            👋 **Welcome to ITER Outlook RAG Chatbot!**
            
            Try asking me anything! 💬
            """)
    
    # 이전 대화 내역 표시
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Assistant 메시지에 출처 문서 표시
            if message["role"] == "assistant" and idx in st.session_state.source_docs:
                with st.expander("📎 View Source Emails"):
                    docs = st.session_state.source_docs[idx]
                    for i, doc in enumerate(docs, 1):
                        meta = doc.metadata
                        title = meta.get("subject_preview", "(No Subject)")
                        sender = meta.get("sender", "(Unknown Sender)")
                        recipients = meta.get("recipients", "(Unknown Recipients)")
                        date = meta.get("date", "(Unknown Date)")
                        content = doc.page_content
                        
                        st.markdown(f"**📧 Email {i}**")
                        st.markdown(f"**From:** `{sender}`")
                        st.markdown(f"**To:** `{recipients}`")
                        st.markdown(f"**Date:** `{date}`")
                        st.markdown(f"**Subject:** {title}")
                        
                        # 내용 미리보기
                        with st.expander(f"📄 View Email Content"):
                            st.text(content[:800] + ('...' if len(content) > 800 else ''))
                        
                        if i < len(docs):
                            st.markdown("---")

# 채팅 입력창 (화면 하단 고정)
if prompt := st.chat_input("💬 Ask about ITER emails... (e.g., What are VV transportation challenges?)"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 즉시 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Assistant 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching emails and generating answer..."):
            # 스마트 검색 (쿼리 분석 + 메타데이터 필터링 + 의미 검색)
            docs = smart_retrieve(prompt)
            
            # 답변 생성
            answer = rag_chain.invoke(prompt)
            
            # 답변 표시
            st.markdown(answer)
            
            # 현재 assistant 메시지 인덱스
            assistant_idx = len(st.session_state.messages)
            
            # 출처 문서 표시
            with st.expander("📎 View Source Emails"):
                for i, doc in enumerate(docs, 1):
                    meta = doc.metadata
                    title = meta.get("subject_preview", "(No Subject)")
                    sender = meta.get("sender", "(Unknown Sender)")
                    recipients = meta.get("recipients", "(Unknown Recipients)")
                    date = meta.get("date", "(Unknown Date)")
                    content = doc.page_content
                    
                    st.markdown(f"**📧 Email {i}**")
                    st.markdown(f"**From:** `{sender}`")
                    st.markdown(f"**To:** `{recipients}`")
                    st.markdown(f"**Date:** `{date}`")
                    st.markdown(f"**Subject:** {title}")
                    
                    # 내용 미리보기
                    with st.expander(f"📄 View Email Content"):
                        st.text(content[:800] + ('...' if len(content) > 800 else ''))
                    
                    if i < len(docs):
                        st.markdown("---")
            
            # Assistant 메시지와 출처 문서 저장
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.source_docs[assistant_idx] = docs