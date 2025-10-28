#!/bin/bash
# ITER Outlook RAG Chatbot 실행 스크립트

echo "🚀 Starting ITER Outlook RAG Chatbot..."
echo ""

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# src 디렉토리로 이동
cd src

# Streamlit 앱 실행
echo "✅ Launching Streamlit app..."
echo ""
echo "📱 The app will open in your browser automatically"
echo "🔗 If not, open: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run rag_streamlit_chatbot.py






