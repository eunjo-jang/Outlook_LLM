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
   git clone <repository-url>
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

## Usage

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

### 3. Data Processing Pipeline

Data processing follows this sequence:

1. **MBOX Conversion** (already completed)
   ```bash
   # After activating virtual environment
   cd scripts
   python mbox_converter.py
   ```

2. **Data Cleaning**
   ```bash
   # After activating virtual environment
   cd scripts
   python data_cleaner.py
   ```

3. **Text Chunking**
   ```bash
   # After activating virtual environment
   cd scripts
   python text_chunker.py
   ```

4. **Vector Index Creation**
   ```bash
   # After activating virtual environment
   cd src
   python vector_index.py
   ```

5. **Data Analysis** (optional)
   ```bash
   # After activating virtual environment
   cd scripts
   python data_analyzer.py
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

## Notes

- This project uses pre-processed data
- To add new email data, you need to re-run the entire pipeline
- Keep your API keys secure
- The system is designed for ITER project email data but can be adapted for other email datasets