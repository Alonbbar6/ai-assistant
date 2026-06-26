# Personal AI Assistant

A local AI assistant built with Python and Claude that can search your files, summarize PDFs, answer questions about documents, manage your Google Calendar, send emails, and accept voice commands.

Built as a portfolio project to demonstrate LLM API integration, RAG, OAuth2, and Python application architecture.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Claude](https://img.shields.io/badge/Claude-claude--sonnet--4--6-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

## Features

| Feature | Description |
|---|---|
| 💬 Chat | Conversational interface powered by Claude |
| 🔍 File Search | Search files on your computer by name or type |
| 📄 PDF Summarization | Extract and summarize PDF documents |
| 🧠 Document Q&A | RAG-powered answers from your indexed documents |
| 📅 Google Calendar | List, create, and delete calendar events |
| 📧 Gmail | Read inbox and send emails |
| 🎙️ Voice | Whisper-powered speech-to-text input |

## Tech Stack

- **LLM** — [Anthropic Claude](https://anthropic.com) via tool-use API
- **RAG** — ChromaDB vector store + sentence-transformers embeddings
- **Google APIs** — Calendar + Gmail via OAuth2
- **Voice** — OpenAI Whisper (local STT) + pyttsx3 (TTS)
- **UI** — Streamlit
- **PDF** — pdfplumber

## Architecture

```
core/agent.py        ← Claude tool-use orchestrator (the brain)
core/memory.py       ← Sliding-window conversation history
tools/
  file_search.py     ← Filesystem search
  pdf_tool.py        ← PDF text extraction
  calendar_tool.py   ← Google Calendar API
  email_tool.py      ← Gmail API
  voice.py           ← Whisper STT + pyttsx3 TTS
rag/
  document_store.py  ← ChromaDB indexing + semantic search
ui/
  streamlit_app.py   ← Web GUI
  cli.py             ← Terminal interface
```

## Setup

### 1. Install dependencies

```bash
bash setup.sh
source .venv/bin/activate
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:
```
ANTHROPIC_API_KEY=sk-ant-...
EMAIL_FROM=your.email@gmail.com
```

### 3. Google OAuth (Calendar + Gmail)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project and enable **Google Calendar API** and **Gmail API**
3. Create **OAuth 2.0 Desktop credentials** → download JSON
4. Save as `credentials/google_credentials.json`

### 4. Run

```bash
# Web GUI (recommended)
bash run_gui.sh

# Terminal CLI
python main.py

# Voice mode
python main.py --voice
```

## Usage Examples

**Chat:**
- *"What's on my calendar this week?"*
- *"Find PDF files on my computer about machine learning"*
- *"Summarize /Users/me/Documents/report.pdf"*
- *"Email john@example.com: Subject: Hello, Body: ..."*

**Document Q&A:**
1. Upload a PDF via the Documents panel in the sidebar
2. Ask: *"What does this document say about X?"*

## Skills Demonstrated

- LLM API integration with tool use / function calling
- Retrieval-Augmented Generation (RAG) pipeline
- OAuth2 authentication flow (Google APIs)
- Multi-turn conversation memory management
- Local speech recognition (Whisper)
- Streamlit web application development
