# Outlook Email RAG System (v3)

This project is a RAG (Retrieval-Augmented Generation) system based on Outlook email data. It uses ChromaDB vector database with LangChain and OpenAI API to provide intelligent question-answering capabilities for email content.

## Project Structure

```
Outlook_LLM_v3/
├── src/                          # Main source code
│   ├── rag_streamlit_chatbot.py # Streamlit web app with RAG
│   ├── rag_chat.py              # RAG chat logic
│   └── build_chromaDB.py        # ChromaDB vector store creation
├── scripts/                      # Utility scripts
│   ├── mbox_converter.py        # MBOX → JSONL conversion
│   ├── data_cleaner.py          # Data cleaning
│   └── chunk_emailwise.py       # Email-wise text chunking
├── data/                         # Data files (not in git)
│   ├── *.jsonl                  # Email data
│   └── vectorstore/             # ChromaDB vector store
├── run_chatbot.sh               # Quick start script
├── requirements.txt             # Dependencies
└── README.md                    # Project documentation
```

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/eunjo-jang/Outlook_LLM.git
   cd Outlook_LLM
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Environment variables setup**
   Create a `.env` file in the root directory and add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```
   
   Get your OpenAI API key from: https://platform.openai.com/api-keys

## Data Preparation

Before using the RAG system, you need to process your Outlook email data. This section describes the complete data processing pipeline from PST files to the final RAG system.

### Prerequisites

Before starting, you need:
- **readpst** tool installed (for PST file conversion)
- **Outlook PST file** containing your email data

### Step-by-Step Data Processing

**Step 1: Install readpst (if not already installed)**
```bash
# On Ubuntu/Debian:
sudo apt-get install readpst

# On macOS:
brew install readpst

# On Windows:
# Download from: https://www.five-ten-sg.com/libpst/
```

**Step 2: Convert PST to MBOX files**
```bash
# Convert PST file to MBOX format
readpst -D -o /path/to/output/directory "/path/to/your/outlook.pst"

# Example:
readpst -D -o /home/user/Outlook_LLM "/mnt/external/MyOutlookData.pst"
```

This command will create multiple `.mbox` files in the output directory, each representing a different Outlook folder.

**Step 3: Convert MBOX to JSONL**
```bash
# After activating virtual environment
cd scripts
python mbox_converter.py
```

This script converts all `.mbox` files to a single `outlook_2021.jsonl` file containing structured email data.

**Step 4: Data Cleaning**
```bash
# After activating virtual environment
cd scripts
python data_cleaner.py
```

This step:
- Removes HTML tags from email bodies
- Filters out spam, newsletters, and auto-replies
- Standardizes date formats
- Removes empty emails
- Outputs `outlook_2021_cleaned.jsonl`

**Step 5: Email-wise Text Chunking**
```bash
# After activating virtual environment
cd scripts
python chunk_emailwise.py
```

This step:
- Splits each email into manageable chunks
- Preserves email metadata (subject, sender, date)
- Outputs `outlook_chunk_emailwise.jsonl`

**Step 6: Vector Database Creation**
```bash
# After activating virtual environment
cd src
python build_chromaDB.py
```

This step:
- Generates embeddings using HuggingFace Sentence Transformers
- Creates ChromaDB vector store for fast similarity search
- Outputs vector database in `data/vectorstore/chroma_outlook/`

### Data Flow Summary

```
PST File → MBOX Files → JSONL → Cleaned JSONL → Chunked JSONL → ChromaDB
    ↓           ↓          ↓           ↓              ↓              ↓
readpst    mbox_converter  data_cleaner  chunk_emailwise  build_chromaDB
```

### File Sizes and Processing Time

- **PST files**: Can be several GB
- **MBOX files**: Similar size to PST
- **JSONL files**: Smaller due to text extraction
- **ChromaDB**: Depends on number of chunks (typically 200-500MB)

Processing time depends on:
- Size of PST file
- Number of emails
- Hardware specifications

## Usage

After completing the data preparation steps above, you can use the RAG chatbot:

### Quick Start (Recommended)
```bash
# Run the startup script
./run_chatbot.sh
```

This script will:
- Activate the virtual environment
- Launch the Streamlit web interface
- Open the chatbot in your browser automatically

### Manual Start
```bash
# After activating virtual environment
source venv/bin/activate
cd src
streamlit run rag_streamlit_chatbot.py
```

The chatbot will be available at `http://localhost:8501`

## Key Features

- **Intelligent Email Search**: Find relevant emails using ChromaDB vector similarity search
- **Contextual Q&A**: Generate accurate answers using RAG with OpenAI GPT-4o
- **Few-Shot Learning**: Improved responses with semantic example selection
- **Chat History**: Maintains conversation context across multiple queries
- **Source Display**: Shows relevant email excerpts used to generate answers
- **Modern UI**: Beautiful, responsive Streamlit interface
- **Email-wise Chunking**: Better context preservation with email-centric chunking

## Technology Stack

- **RAG Framework**: LangChain
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: OpenAI GPT-4o
- **Web Framework**: Streamlit
- **Data Processing**: NLTK, BeautifulSoup, python-dateutil

## Project Background

This RAG system is designed for the ITER Vacuum Vessel project, enabling efficient search and analysis of project-related email communications. The v3 version represents a major refactor with improved chunking strategy, ChromaDB integration, and enhanced UI/UX.
