# Outlook Email RAG System

This project is a RAG (Retrieval-Augmented Generation) system based on Outlook email data. It uses FAISS vector indexing and OpenAI API to provide question-answering capabilities for email content.

## Project Structure

```
Outlook_LLM/
├── src/                    # Main source code
│   ├── email_rag.py       # RAG system core logic
│   ├── cli.py             # CLI interface
│   ├── web_app.py         # Streamlit web app
│   ├── vector_index.py    # FAISS index creation
│   └── config.py          # Configuration file
├── scripts/               # Utility scripts
│   ├── mbox_converter.py  # MBOX → JSONL conversion
│   ├── text_chunker.py    # Text chunking
│   ├── data_cleaner.py    # Data cleaning
│   └── data_analyzer.py   # Data analysis
├── data/                  # Data files
│   ├── *.jsonl           # Email data
│   └── faiss_index.bin   # Vector index
├── requirements.txt       # Dependencies
└── README.md             # Project documentation
```

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/eunjo-jang/Outlook_RAG_v1.git
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
   OPENAI_MODEL=gpt-4o
   ```
   
   You can use the `env.example` file as a template. See the file for detailed instructions on how to obtain an OpenAI API key.

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

**Step 5: Text Chunking**
```bash
# After activating virtual environment
cd scripts
python text_chunker.py
```

This step:
- Splits long email bodies into smaller chunks (max 1000 characters)
- Adds overlap between chunks (200 characters)
- Preserves email metadata (subject, sender, date)
- Outputs `emails_chunked.jsonl`

**Step 6: Vector Index Creation**
```bash
# After activating virtual environment
cd src
python vector_index.py
```

This step:
- Generates embeddings for all text chunks using Sentence Transformers
- Creates FAISS vector index for fast similarity search
- Outputs `faiss_index.bin`

**Step 7: Data Analysis (Optional)**
```bash
# After activating virtual environment
cd scripts
python data_analyzer.py
```

This provides statistics about your email dataset (length distribution, etc.).

### Data Flow Summary

```
PST File → MBOX Files → JSONL → Cleaned JSONL → Chunked JSONL → Vector Index
    ↓           ↓          ↓           ↓              ↓              ↓
readpst    mbox_converter  data_cleaner  text_chunker  vector_index
```

### File Sizes and Processing Time

- **PST files**: Can be several GB
- **MBOX files**: Similar size to PST
- **JSONL files**: Smaller due to text extraction
- **Vector index**: Depends on number of chunks (typically 200-500MB)

Processing time depends on:
- Size of PST file
- Number of emails
- Hardware specifications (GPU recommended for vector indexing)

## Usage

After completing the data preparation steps above, you can use the RAG system in two ways:

### 1. CLI Interface
```bash
# After activating virtual environment
cd src
python cli.py
```

### 2. Web App (Streamlit)
```bash
# After activating virtual environment
cd src
streamlit run web_app.py
```

## Key Features

- **Email Search**: Find relevant emails using FAISS vector search
- **Question-Answering**: Generate answers using OpenAI GPT models
- **Model Selection**: Choose from various OpenAI models (GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo)
- **Web Interface**: User-friendly UI with Streamlit
- **CLI Interface**: Quick question-answering via command line

## Technology Stack

- **Vector Search**: FAISS
- **Embeddings**: Sentence Transformers
- **LLM**: OpenAI GPT models
- **Web Framework**: Streamlit
- **Data Processing**: NLTK, BeautifulSoup, python-dateutil

## Evaluation

The project includes an evaluation dataset (`evaluation_analysis.md`) with 15 question-answer pairs to test the RAG system's performance on both conceptual questions and specific information retrieval tasks.
