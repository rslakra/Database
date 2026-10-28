# Vector Database

Vector database tooling for local development under `Database/VectorDatabases`.

## Unified admin UI (Tuplex)

Use **[Tuplex/](Tuplex/)** as the single local admin UI for vector and relational databases. Connect to ChromaDB, MySQL, and more from one interface.

```bash
cd Database/VectorDatabases/Tuplex
cp .env.example .env
# configure admin user — see Tuplex/README.md
./start.sh
```

Open http://127.0.0.1:8500 → sign in → connect to your database.

## Available Backends

| Backend | Path | Description |
|---------|------|-------------|
| Folio | [Folio/](Folio/) | Standalone FastAPI app — upload docs, Chroma Q&A, backup/reset, export |
| Chroma | [Chroma/](Chroma/) | Official `chromadb/chroma` Docker server; GUI via browser UI |
| Weaviate | [Weaviate/](Weaviate/) | Official `semitechnologies/weaviate` Docker server; GUI via Weaviate Console |
| Pinecone | [Chroma/Pinecone/](Chroma/Pinecone/) | Official `pinecone-local` Docker emulator for dev/CI (in-memory) |

## Quick Start

**Chroma** (port 8000):

```bash
cd Database/VectorDatabases/Chroma
chmod +x start.sh stop.sh
./start.sh
```

**Weaviate** (port 8080):

```bash
cd Database/VectorDatabases/Weaviate
chmod +x start.sh stop.sh
./start.sh
```

**Pinecone Local** (port 5080):

```bash
cd Database/VectorDatabases/Chroma/Pinecone
chmod +x start.sh stop.sh
./start.sh
```

## How to Choose Vector Dimensions (Powers of 2)

**2^10 (1024 dimensions)** is the best default for general embedding workflows. It balances search accuracy, retrieval speed, and memory usage.

### Standard powers of 2

Vector databases and hardware are optimized for binary processing, so powers of 2 are the industry standard.

| Power | Dimensions | Typical use |
|-------|------------|-------------|
| 2^8 | 256 | Highly compressed, low-memory models or lightweight text/sentence fragments |
| 2^9 | 512 | Lightweight open-source models (e.g. some BERT or MiniLM variants) tuned for speed |
| 2^10 | 1024 | **Sweet spot** — used by many commercial models (e.g. Cohere) and major open-source embeddings |
| 2^11 | 2048 | Complex multi-lingual or multi-modal datasets (text + images) |

### Why use powers of 2?

**1. Match your hardware architecture**

Modern CPUs and GPUs process data in parallel chunks based on binary blocks (32, 64, or 128 bits). Setting vector dimensions to a power of 2 aligns database math with memory registers, reduces waste, and improves throughput during distance calculations (cosine, Euclidean, etc.).

**2. Balance the curse of dimensionality**

As dimensions grow, distances between vectors become less distinct and search accuracy can degrade. Around **1024 dimensions**, the vector space is large enough to separate complex concepts but small enough to stay efficient.

**3. Estimate memory consumption**

Vectors are usually stored as 32-bit floats (4 bytes each). Memory per vector is easy to calculate:

```
1024 dimensions × 4 bytes = 4096 bytes (4 KB per vector)
```

At 1024 dimensions, **1,000,000 vectors** need roughly **4 GB** of raw RAM for the embeddings alone.

### Summary

For most projects, **1024 dimensions (2^10)** is the best balance of performance, hardware alignment, and accuracy. Pick a lower dimension when memory or latency matters most; pick 2048 when you need richer multi-modal or multi-lingual representations.

## Backend Docs

- [Folio/README.md](Folio/README.md) — web UI for document upload, Q&A, backup, and export
- [Chroma/README.md](Chroma/README.md) — GUI access, API usage, troubleshooting
- [Weaviate/README.md](Weaviate/README.md) — console access, API usage, troubleshooting
- [Chroma/Pinecone/README.md](Chroma/Pinecone/README.md) — local emulator limits, API usage, troubleshooting
