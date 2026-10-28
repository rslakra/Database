# VectorDbDemo

Jupyter notebook demo for **ChromaDB + LangChain** — load TechCrunch articles, embed them locally, store vectors on disk, and run retrieval Q&A with a Hugging Face LLM.

## Notebooks

| Notebook | Description |
|----------|-------------|
| [Complete Vector Database Tutorial.ipynb](%20Complete%20Vector%20Database%20Tutorial.ipynb) | End-to-end Chroma setup: document loading, chunking, local embeddings, similarity search, and a QA chain |
| [Folio](../Folio/) | **FastAPI web app (Folio)** — upload docs, configure Chroma, Q&A, backup/reset, export PDF/Markdown/JSON |

## What the notebook does

1. **Load documents** — `DirectoryLoader` reads `.txt` files from `./Articles/`
2. **Chunk text** — `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap)
3. **Embed & store** — `open_or_create_vectordb()` opens an existing index, restores from zip, or creates fresh in `./chroma-local-db/`
4. **Retrieve** — vector similarity search via `retriever.invoke(...)`
5. **Answer questions** — LangChain `create_retrieval_chain` + local **TinyLlama** LLM

All embeddings and LLM inference run **locally**. No OpenAI key is required.

## Prerequisites

- Python 3.10+ (3.14 tested)
- Hugging Face token — free at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Sample articles in `./Articles/` (included in the repo)
- Optional: [uv](https://docs.astral.sh/uv/) CLI (`make uv` installs it on your system)

### uv vs pip (they are not linked)

| Tool | What it is | Used for in this project |
|------|------------|--------------------------|
| **uv** | System-wide Python tool installer (`~/.local/bin/uv`) | Installed by `make uv` if you want it available |
| **pip** | Package manager inside `venv/` | Installs notebook dependencies (`make install`) |

`make setup` installs **both**, but they do separate jobs: uv goes on your machine, pip manages packages in `venv/`.

## Environment variables

Create `VectorDbDemo/.env` from the sample:

```bash
cp .env.sample .env
# edit .env and set HF_TOKEN=hf_...
```

Or create it manually:

| Variable | Required | Purpose |
|----------|----------|---------|
| `HF_TOKEN` | Yes (for QA chain) | Download Hugging Face models; used by embeddings + LLM |
| `ANONYMIZED_TELEMETRY` | Optional | Disable Chroma telemetry noise |

The notebook loads `.env` via `chroma_utils.load_project_env()`, which finds `VectorDbDemo/.env` even when Jupyter’s working directory is the parent folder.

## First-time setup

```bash
cd Database/VectorDatabases/VectorDbDemo
make setup
source venv/bin/activate
```

This will:

1. Install `uv` CLI (optional)
2. Create `venv/` with `python -m venv`
3. `pip install -r requirements.txt`
4. Register Jupyter kernel **Vector DB Demo**

### Key dependencies (pinned in `requirements.txt`)

| Package | Role |
|---------|------|
| `chromadb` 0.4.x | Vector database |
| `posthog` 3.x | Required by Chroma 0.4 (avoid 7.x API break) |
| `langchain` 0.1.x | Chains, retrievers |
| `langchain-community` | Chroma, HuggingFace embeddings/LLM |
| `sentence-transformers` | Local embedding model |
| `transformers` | Local TinyLlama LLM for QA |

## Run the notebooks

```bash
make notebook
```

In Jupyter: **Kernel → Change kernel → Vector DB Demo**

### Use the correct kernel (important)

| Picker section | Example | Uses |
|----------------|---------|------|
| **Jupyter Kernel** | Vector DB Demo | `VectorDbDemo/venv/` ✅ |
| **Python Environments** | `.venv (Python 3.12)` | `Services/.venv/` ❌ |

Verify in the first cell:

```python
import sys
print(sys.executable)
# .../VectorDbDemo/venv/bin/python
```

**Open this folder as your workspace** (not the parent `Services/` repo):

```bash
cd Database/VectorDatabases/VectorDbDemo
cursor .
```

Re-register the kernel if needed:

```bash
make kernel
```

## Project helpers (`chroma_utils.py`)

Shared utilities used by the notebook:

| Function | Purpose |
|----------|---------|
| `load_project_env()` | Load `.env` from project root |
| `make_client_settings()` | Chroma settings + disabled telemetry |
| `clear_chroma_cache()` | Safe re-run of Chroma cells in same kernel |
| `open_or_create_vectordb()` | Open existing DB, restore from zip, or create + embed (section 7) |
| `get_hf_llm()` | Local TinyLlama LLM using `HF_TOKEN` |
| `archive_persist_directory()` | Zip `./chroma-local-db/` for backup |
| `reset_persist_directory()` | Delete on-disk database (section 10) |

## Troubleshooting

### `HF_TOKEN not found`
- Add `HF_TOKEN=hf_...` to `VectorDbDemo/.env`
- Re-run the environment cell or any cell that calls `chroma_utils.load_project_env()`

### Chroma “already exists with different settings”
- Re-run the cell that calls `chroma_utils.clear_chroma_cache()` before creating/reopening the DB

### Hugging Face Hub warnings (unauthenticated)
- Set `HF_TOKEN` in `.env` — removes “unauthenticated requests” warnings on model download

### `zip: command not found` / wrong path when backing up Chroma
- Use the notebook’s archive cell — it calls `chroma_utils.archive_persist_directory()` (Python `shutil`, no shell `zip` needed)

### First QA run is slow
- TinyLlama (~1.1B) downloads once (~2 GB); later runs use the cached model

## Make targets

| Target | Description |
|--------|-------------|
| `setup` | Full first-time setup (uv + venv + pip + kernel) |
| `uv` | Install uv CLI |
| `venv` | Create `venv/` |
| `install` | `pip install -r requirements.txt` |
| `kernel` | Register Jupyter kernel |
| `notebook` | Launch Jupyter |
| `clean` | Remove `venv/` and `__pycache__` |

## Manual setup (without Make)

```bash
cd Database/VectorDatabases/VectorDbDemo

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name=vector-db-demo --display-name="Vector DB Demo"
jupyter notebook
```

## Notes

- Chroma 0.4+ **auto-persists** — `vectordb.persist()` is deprecated and not used.
- LangChain 0.1.x APIs: `retriever.invoke(...)`, `create_retrieval_chain`, `langchain_community` imports.
- The original Colab notebook downloaded articles at runtime; this repo includes `./Articles/` locally.
