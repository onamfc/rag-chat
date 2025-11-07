# Xantus - Private RAG Chat System with MCP Integration

<div align="center">

**A production-ready RAG (Retrieval Augmented Generation) system for chatting with your documents**

*Built with privacy in mind • Extensible via MCP • Multi-provider AI support*

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [MCP Integration](#mcp-integration) • [Configuration](#configuration) • [API Reference](#api-reference)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [First Run](#first-run)
- [MCP Integration](#mcp-integration)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Provider Setup](#provider-setup)
  - [RAG Tuning](#rag-tuning)
- [Usage](#usage)
  - [Streamlit UI](#streamlit-ui)
  - [API Endpoints](#api-endpoints)
  - [Python Client](#python-client)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)

---

## Overview

Xantus is a **privacy-first** RAG system that lets you chat with your documents using AI. Unlike cloud-only solutions, Xantus can run **completely locally** or use cloud providers - your choice.

### What Makes Xantus Different?

- **Privacy-First**: All data stays on your system with local AI
- **Extensible**: MCP (Model Context Protocol) integration for external tools
- **Multiple UIs**: Streamlit interface + OpenAI-compatible API
- **Multi-Provider**: Supports Ollama, OpenAI, Anthropic, and more
- **Modular**: Swap LLMs, embeddings, vector stores easily
- **Production-Ready**: Dependency injection, proper error handling, logging

---

## Features

### Core Features

- **Document Chat**: Upload PDFs, DOCX, TXT, Markdown and chat with them
- **Semantic Search**: RAG-powered retrieval with ChromaDB or Qdrant
- **Multiple Interfaces**:
  - Clean Streamlit UI for end users
  - RESTful API for integration
  - Python SDK for developers
- **Flexible AI Backends**:
  - **Local**: Ollama (privacy-first)
  - **Cloud**: OpenAI, Anthropic
  - **Hybrid**: Cloud LLM + local embeddings

### Advanced Features

- **MCP Integration**: Connect external tools (calculator, file system, databases)
- **⚙Configurable**: YAML + environment variables
- **Multiple Vector Stores**: ChromaDB, Qdrant
- **RAG Tuning**: Adjust chunk size, overlap, top-k retrieval
- **Secure**: API key management via environment variables
- **Scalable**: Async API with proper dependency injection

---

## Architecture

Xantus is built on a modern, modular architecture:

```
┌─────────────────────────────────────────────────────────┐
│                        User                             │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    ┌────────▼────────┐          ┌────────▼─────────┐
    │  Streamlit UI   │          │   API Clients    │
    │  (Port 8501)    │          │   (curl, SDK)    │
    └────────┬────────┘          └────────┬─────────┘
             │                            │
             └────────────┬───────────────┘
                          │
                 ┌────────▼─────────┐
                 │   FastAPI Server │
                 │   (Port 8000)    │
                 └────────┬─────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
   ┌──────▼──────┐ ┌──────▼───────┐ ┌────▼─────┐
   │ Chat Service│ │Ingest Service│ │   MCP    │
   └──────┬──────┘ └──────┬───────┘ │ Service  │
          │               │         └────┬─────┘
          │               │              │
   ┌──────▼───────────────▼──────────────▼─────┐
   │        Dependency Injection Container     │
   │  (LLM • Embeddings • Vector Store • MCP)  │
   └────────────────────┬──────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌─────▼─────┐   ┌───▼────┐
   │   LLM   │    │ Embeddings│   │ Vector │
   │Provider │    │  Provider │   │ Store  │
   └─────────┘    └───────────┘   └────────┘
   │Ollama   │    │HuggingFace│   │Chroma  │
   │OpenAI   │    │  Ollama   │   │Qdrant  │
   │Anthropic│    │  OpenAI   │   └────────┘
   └─────────┘    └───────────┘
                                   ┌──────────┐
                                   │MCP Server│
                                   │TypeScript│
                                   └──────────┘
                                   │Calculator│
                                   │FileSystem│
                                   │TextProc  │
                                   └──────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Python 3.10+ | High-performance async API |
| **RAG Framework** | LlamaIndex | Document indexing & retrieval |
| **UI** | Streamlit | User-friendly chat interface |
| **Configuration** | Pydantic + YAML | Type-safe settings |
| **DI** | Injector | Clean dependency injection |
| **Vector DB** | ChromaDB / Qdrant | Semantic search |
| **MCP** | Model Context Protocol | External tool integration |

### Project Structure

```
xantus/
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore patterns
├── config.yaml                   # Main configuration file
├── requirements.txt              # Python dependencies
├── setup_mcp.sh                 # MCP setup automation
├── start_api.sh                 # API server startup script
├── start_ui.sh                  # UI startup script
│
├── xantus/                       # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry
│   ├── container.py             # Dependency injection setup
│   │
│   ├── api/                     # API endpoints
│   │   ├── chat_router.py       # /v1/chat/completions
│   │   ├── ingest_router.py     # /v1/ingest/*
│   │   └── embeddings_router.py # /v1/embeddings
│   │
│   ├── services/                # Business logic
│   │   ├── chat_service.py      # RAG-powered chat
│   │   ├── ingest_service.py    # Document processing
│   │   └── mcp_service.py       # MCP tool orchestration
│   │
│   ├── components/              # Component factories
│   │   ├── llm/
│   │   │   └── llm_factory.py   # LLM provider factory
│   │   ├── embeddings/
│   │   │   └── embedding_factory.py
│   │   └── vector_store/
│   │       └── vector_store_factory.py
│   │
│   ├── models/                  # Data models
│   │   └── schemas.py           # Pydantic request/response models
│   │
│   └── config/                  # Configuration
│       └── settings.py          # Settings management with Pydantic
│
├── ui/                          # User interface
│   └── streamlit_app.py         # Streamlit chat application
│
├── mcp-servers/                 # MCP integration (git submodules)
│   └── mcp-starter-template-ts/ # TypeScript MCP server
│       ├── dist/                # Compiled JavaScript
│       │   └── start.js         # Entry point
│       └── src/                 # TypeScript source
│           └── tools/           # Tool implementations
│
├── data/                        # Data directory (gitignored)
│   └── vector_store/            # Persisted vector embeddings
│
└── docs/                        # Documentation
    ├── MCP_INTEGRATION.md       # MCP technical guide
    ├── README_MCP.md            # MCP quick start
    └── SETUP_COMPLETE.md        # Setup summary
```

---

## Quick Start

### Prerequisites

- **Python 3.10+** (Check: `python --version`)
- **Node.js 18+** (For MCP integration, check: `node --version`)
- **Git** (For cloning submodules)
- **(Optional) Ollama** (For local AI)

### Installation

#### Step 1: Clone the Repository

```bash
# Clone with MCP submodules
git clone --recurse-submodules https://github.com/onamfc/rag-chat
cd xantus

# OR if you already cloned without submodules:
git submodule update --init --recursive
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

#### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Setup MCP (Optional but Recommended)

```bash
# This will:
# - Initialize MCP submodules
# - Install npm dependencies
# - Build TypeScript MCP server
./setup_mcp.sh
```

#### Step 5: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys (if using cloud providers)
# For Anthropic:
XANTUS_LLM__API_KEY=sk-ant-api03-your-key-here

# For OpenAI:
# XANTUS_LLM__API_KEY=sk-your-openai-key-here
```

#### Step 6: Configure Settings

Edit `config.yaml` to choose your providers:

**Option A: Completely Local (Privacy-First)**
```yaml
llm:
  provider: ollama
  model: llama3.2

embedding:
  provider: huggingface
  model: BAAI/bge-small-en-v1.5

mcp:
  enabled: true  # Enable MCP tools
```

**Option B: Cloud-Powered (Anthropic)**
```yaml
llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  api_key: null  # Read from .env

embedding:
  provider: huggingface  # Keep embeddings local
  model: BAAI/bge-small-en-v1.5

mcp:
  enabled: true
```

**Option C: OpenAI**
```yaml
llm:
  provider: openai
  model: gpt-4
  api_key: null  # Read from .env

embedding:
  provider: openai
  model: text-embedding-3-small
  api_key: null
```

### First Run

#### Start the API Server

```bash
# Option 1: Using the startup script
./start_api.sh

# Option 2: Manual start
python -m xantus.main

# The API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

You should see:
```
INFO - Starting Xantus application...
INFO - Loaded settings with LLM provider: anthropic
INFO - Dependency injection container initialized
INFO - Starting server on 127.0.0.1:8000
```

With MCP enabled, you'll also see:
```
INFO - Starting MCP server 'mcp-starter-template': node mcp-servers/...
INFO - Loaded 4 tools from 'mcp-starter-template': ['calculate', 'filesystem', 'text-processing', 'weather']
```

#### Start the UI (In a New Terminal)

```bash
# Activate venv again
source venv/bin/activate

# Start Streamlit
streamlit run ui/streamlit_app.py

# The UI will open in your browser at http://localhost:8501
```

#### Upload a Document and Chat!

1. Click **"Upload Document"** in the sidebar
2. Select a PDF, TXT, DOCX, or Markdown file
3. Wait for processing (you'll see the progress)
4. Ask questions about your document!

**Example Questions:**
- "What is the main topic of this document?"
- "Summarize the key points"
- "Calculate the total revenue mentioned in section 3" (uses MCP calculator)
- "Compare this with the file in ../reports/2023.pdf" (uses MCP filesystem)

---

## MCP Integration

MCP (Model Context Protocol) allows Claude to use external tools while answering questions.

### What Tools Are Available?

Your TypeScript MCP server (in `mcp-servers/mcp-starter-template-ts/`) provides:

| Tool | Function | Example Use |
|------|----------|-------------|
| **Calculator** | Mathematical operations | "Calculate the sum of Q1-Q4 revenues" |
| **File System** | Read/write/list files | "Compare with last year's report in ../reports/" |
| **Text Processing** | Word count, sentiment, case conversion | "Analyze sentiment of customer feedback" |
| **Weather** | Weather data (mock) | "Check weather for event planning" |

### MCP Architecture

```
User Question
     ↓
Xantus retrieves document context (RAG)
     ↓
Sends to Claude with available MCP tools
     ↓
Claude decides to use a tool (e.g., calculator)
     ↓
Xantus forwards tool call to MCP server (TypeScript)
     ↓
MCP server executes tool and returns result
     ↓
Claude incorporates result into answer
     ↓
User gets comprehensive response
```

### Enabling/Disabling MCP

In `config.yaml`:

```yaml
mcp:
  enabled: true  # Set to false to disable MCP

  servers:
    - name: "mcp-starter-template"
      command: "node"
      args: ["mcp-servers/mcp-starter-template-ts/dist/start.js"]
```

### Adding More MCP Servers

You can connect multiple MCP servers:

```yaml
mcp:
  enabled: true
  servers:
    # Your custom tools
    - name: "my-tools"
      command: "node"
      args: ["mcp-servers/mcp-starter-template-ts/dist/start.js"]

    # Database access
    - name: "postgres"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]

    # Web search
    - name: "brave-search"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-brave-search"]
```

### MCP Documentation

For complete MCP setup and customization:
- **Quick Start**: [`README_MCP.md`](./README_MCP.md)
- **Technical Guide**: [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md)
- **Setup Summary**: [`SETUP_COMPLETE.md`](./SETUP_COMPLETE.md)

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# ===== LLM API Keys =====
# For Anthropic (double underscore for nested config!)
XANTUS_LLM__API_KEY=sk-ant-api03-your-key-here

# For OpenAI
# XANTUS_LLM__API_KEY=sk-your-openai-key-here

# ===== Embedding API Keys (optional) =====
# XANTUS_EMBEDDING__API_KEY=sk-your-key-here

# ===== Override Other Settings =====
# Format: XANTUS_<SECTION>__<KEY>=value
# Examples:
# XANTUS_LLM__TEMPERATURE=0.5
# XANTUS_RAG__SIMILARITY_TOP_K=10
# XANTUS_SERVER__PORT=8001
```

**Important**: Use **double underscore** (`__`) for nested configuration!

### Provider Setup

#### Local Setup with Ollama

1. **Install Ollama**: https://ollama.com/download

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Pull Models**:
   ```bash
   ollama pull llama3.2        # For chat
   ollama pull nomic-embed-text # For embeddings
   ```

4. **Configure** `config.yaml`:
   ```yaml
   llm:
     provider: ollama
     model: llama3.2
     api_base: http://localhost:11434  # Default

   embedding:
     provider: ollama
     model: nomic-embed-text
   ```

#### Anthropic Setup

1. **Get API Key**: https://console.anthropic.com/

2. **Add to `.env`**:
   ```bash
   XANTUS_LLM__API_KEY=sk-ant-api03-your-key-here
   ```

3. **Configure** `config.yaml`:
   ```yaml
   llm:
     provider: anthropic
     model: claude-sonnet-4-20250514
     api_key: null  # Read from environment
     temperature: 0.7
     max_tokens: 4096

   embedding:
     provider: huggingface  # Use local for cost savings
     model: BAAI/bge-small-en-v1.5
   ```

#### OpenAI Setup

1. **Get API Key**: https://platform.openai.com/api-keys

2. **Add to `.env`**:
   ```bash
   XANTUS_LLM__API_KEY=sk-your-openai-key-here
   ```

3. **Configure** `config.yaml`:
   ```yaml
   llm:
     provider: openai
     model: gpt-4-turbo-preview
     api_key: null

   embedding:
     provider: openai
     model: text-embedding-3-small
     api_key: null
   ```

### RAG Tuning

Fine-tune retrieval in `config.yaml`:

```yaml
rag:
  # Number of relevant chunks to retrieve
  similarity_top_k: 5

  # Size of text chunks (characters)
  chunk_size: 1024

  # Overlap between chunks (prevents context loss)
  chunk_overlap: 200

  # Enable advanced reranking (requires additional setup)
  enable_reranking: false
```

**Tuning Guidelines**:
- **Larger chunks** (1024-2048): Better for long-form content
- **Smaller chunks** (512-1024): Better for specific facts
- **Higher top_k** (8-10): More context but slower
- **Lower top_k** (3-5): Faster but may miss context
- **Overlap**: 15-20% of chunk_size is recommended

### Vector Store Configuration

```yaml
vector_store:
  provider: chroma  # or qdrant

  # Path to persist vector data
  persist_path: ./data/vector_store

  # Collection name
  collection_name: xantus_documents
```

### Server Configuration

```yaml
server:
  host: 127.0.0.1  # Change to 0.0.0.0 for network access
  port: 8000

  # CORS settings
  cors_enabled: true
  cors_origins:
    - "*"  # Be more restrictive in production!
```

---

## Usage

### Streamlit UI

The easiest way to use Xantus:

1. **Start the API** (terminal 1):
   ```bash
   ./start_api.sh
   ```

2. **Start the UI** (terminal 2):
   ```bash
   ./start_ui.sh
   # OR
   streamlit run ui/streamlit_app.py
   ```

3. **Navigate to** http://localhost:8501

4. **Upload documents** via the sidebar

5. **Chat** with your documents!

**Features**:
- ✅ Document upload with progress
- ✅ Document management (list/delete)
- ✅ Chat history
- ✅ Context toggle (use RAG or not)
- ✅ Health monitoring

### API Endpoints

#### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "components": {
    "llm": "anthropic",
    "embedding": "huggingface",
    "vector_store": "chroma"
  }
}
```

#### Chat Completion (with RAG)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the main findings in the report?"}
    ],
    "use_context": true,
    "stream": false
  }'
```

Response:
```json
{
  "id": "chat-123abc",
  "object": "chat.completion",
  "created": 1730000000,
  "model": "claude-sonnet-4-20250514",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Based on the documents, the main findings are..."
    },
    "finish_reason": "stop"
  }]
}
```

#### Upload Document

```bash
curl -X POST http://localhost:8000/v1/ingest/file \
  -F "file=@/path/to/document.pdf"
```

Response:
```json
{
  "status": "success",
  "document_id": "doc_abc123",
  "chunks_created": 42
}
```

#### List Documents

```bash
curl http://localhost:8000/v1/ingest/documents
```

#### Delete Document

```bash
curl -X DELETE http://localhost:8000/v1/ingest/documents/doc_abc123
```

#### Generate Embeddings

```bash
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "Text to embed", "model": "default"}'
```

### Python Client

```python
import requests

# Start a session
session = requests.Session()
api_url = "http://localhost:8000"

# Upload a document
with open("document.pdf", "rb") as f:
    response = session.post(
        f"{api_url}/v1/ingest/file",
        files={"file": f}
    )
    print(f"Uploaded: {response.json()}")

# Chat with RAG
response = session.post(
    f"{api_url}/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Summarize the key points"}
        ],
        "use_context": True,
        "stream": False
    }
)

result = response.json()
print(result["choices"][0]["message"]["content"])
```

---

## Development

### Project Philosophy

1. **Privacy First**: Default to local, support cloud
2. **Modularity**: Easy to swap any component
3. **Simplicity**: Minimal abstractions
4. **Type Safety**: Pydantic everywhere
5. **Production Ready**: Proper DI, error handling, logging

### Adding a New LLM Provider

1. **Add to settings** (`xantus/config/settings.py`):
   ```python
   provider: Literal["ollama", "openai", "anthropic", "your-provider"]
   ```

2. **Implement factory** (`xantus/components/llm/llm_factory.py`):
   ```python
   def _create_your_provider_llm(config: LLMConfig) -> LLM:
       return YourProviderLLM(
           model=config.model,
           api_key=config.api_key,
           temperature=config.temperature
       )
   ```

3. **Update factory dispatch**:
   ```python
   elif config.provider == "your-provider":
       return _create_your_provider_llm(config)
   ```

### Adding a New Vector Store

Similar process in `xantus/components/vector_store/vector_store_factory.py`

### Code Style

```bash
# Format code
black xantus/

# Lint
ruff check xantus/

# Type check
mypy xantus/
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

---

## Troubleshooting

### Common Issues

#### 1. "Cannot connect to Ollama"

**Solution**: Ensure Ollama is running
```bash
ollama serve
```

#### 2. "ValueError: Anthropic API key is required"

**Solution**: Check your `.env` file:
```bash
# Correct (double underscore!):
XANTUS_LLM__API_KEY=sk-ant-...

# Wrong (single underscore):
XANTUS_LLM_API_KEY=sk-ant-...
```

#### 3. "Import error: No module named 'xantus'"

**Solution**: Ensure you're in the right directory
```bash
cd xantus
python -c "import xantus; print('OK')"
```

#### 4. "MCP server not starting"

**Solution**: Build the MCP server
```bash
./setup_mcp.sh
# OR manually:
cd mcp-servers/mcp-starter-template-ts
npm install
npm run build
```

#### 5. "Port 8000 already in use"

**Solution**: Kill existing processes or change port
```bash
# Kill existing
pkill -f "python.*xantus"

# OR change port in config.yaml:
server:
  port: 8001
```

#### 6. "Vector store errors"

**Solution**: Clear and recreate
```bash
rm -rf data/vector_store
mkdir -p data/vector_store
# Restart server, re-upload documents
```

### Debug Mode

Enable verbose logging:

```python
# In xantus/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## FAQ

**Q: Does my data leave my machine?**
A: Only if you use cloud providers (OpenAI/Anthropic). With Ollama + HuggingFace, everything stays local.

**Q: Which is faster - local or cloud?**
A: Cloud (OpenAI/Anthropic) is usually faster. Local (Ollama) depends on your hardware.

**Q: Can I use multiple documents?**
A: Yes! Upload as many as you want. They're all indexed in the vector store.

**Q: What's the maximum document size?**
A: No hard limit, but larger documents take longer to process.

**Q: Can I delete documents?**
A: Yes, via the API `/v1/ingest/documents/{doc_id}` or Streamlit UI.

**Q: Is streaming supported?**
A: Yes! Set `"stream": true` in chat completion requests.

**Q: What LLM is best?**
A:
- **Best quality**: Claude Sonnet 4, GPT-4
- **Best local**: Llama 3.2, Mistral
- **Best balance**: Claude Haiku, GPT-3.5-turbo

**Q: How do I add authentication?**
A: Add FastAPI middleware in `xantus/main.py` for API key or OAuth.

---

## Additional Resources

- **MCP Integration Guide**: [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md)
- **MCP Quick Start**: [`README_MCP.md`](./README_MCP.md)
- **API Documentation**: http://localhost:8000/docs (when running)
- **LlamaIndex Docs**: https://docs.llamaindex.ai/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

## Contributing

Contributions are welcome! This project is designed to be:
- Easy to understand
- Simple to extend
- Well-documented

Feel free to:
- Add new providers
- Improve the UI
- Enhance MCP tools
- Fix bugs
- Improve documentation

---

## License

This project is provided as-is for educational and research purposes.

---

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern async web framework
- [LlamaIndex](https://www.llamaindex.ai/) - RAG framework
- [Streamlit](https://streamlit.io/) - Data apps framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Ollama](https://ollama.com/) - Local LLM runtime
- [Model Context Protocol](https://modelcontextprotocol.io/) - Tool integration

---

<div align="center">

**Made with ❤️ for the open source community**

[⬆ Back to Top](#xantus---private-rag-chat-system-with-mcp-integration)

</div>
