# Pinecone Local (Vector Database Emulator)

Local development using **Pinecone Local** — Pinecone's official in-memory Docker emulator (`ghcr.io/pinecone-io/pinecone-local`).

## What You Get

| Service | URL | Purpose |
|---------|-----|---------|
| Pinecone Local API | http://localhost:5080 | Database emulator (create/manage indexes via API) |
| Index ports | 5080–5090 | Ports assigned to indexes created at runtime |

Pinecone Local is for **local development and testing only**. Data is in-memory and **does not persist** after the container stops. For production, use [Pinecone Cloud](https://www.pinecone.io/).

## Official vs Cloud

| Option | Official? | Notes |
|--------|-----------|-------|
| `ghcr.io/pinecone-io/pinecone-local` | Yes | Full database emulator; create indexes via API |
| `ghcr.io/pinecone-io/pinecone-index` | Yes | Single pre-configured index on startup (simpler, less flexible) |
| Pinecone Cloud | Yes | Managed production service |

This setup uses `pinecone-local` so you can create and manage indexes like production, without a Pinecone account.

## Limitations (Pinecone Local)

- In-memory only — no persistence across restarts
- API keys are ignored (pass any string, e.g. `pclocal`)
- Max **100,000** records per index
- Uses API version `2025-01`; requires Python SDK **v6.x+**

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)
- On Apple Silicon Macs, `platform: linux/amd64` is set in `docker-compose.yml` (emulation may be slower)

## Quick Start

```bash
cd Database/VectorDatabases/Pinecone
chmod +x start.sh stop.sh
./start.sh
```

Stop the stack:

```bash
./stop.sh
```

## Verify API Access (CLI)

```bash
cd Database/VectorDatabases/Pinecone
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_connection.py
```

Expected output confirms connection and lists indexes (empty on first run).

## Programmatic Access (Python)

```python
from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone import ServerlessSpec

pc = PineconeGRPC(api_key="pclocal", host="http://localhost:5080")

index_name = "docs"
if not pc.has_index(index_name):
  pc.create_index(
    name=index_name,
    vector_type="dense",
    dimension=1024,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
  )

index_host = pc.describe_index(name=index_name).host
index = pc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))

index.upsert(
  vectors=[
    {"id": "1", "values": [0.1] * 1024, "metadata": {"text": "Pinecone Local on Docker."}},
    {"id": "2", "values": [0.2] * 1024, "metadata": {"text": "Vector search without the cloud."}},
  ]
)

results = index.query(vector=[0.1] * 1024, top_k=1, include_metadata=True)
print(results)
```

Use **1024** dimensions to match common embedding models (see [VectorDatabases/README.md](../README.md)).

## GUI

Pinecone does not ship a local admin GUI container. Use the [Pinecone console](https://app.pinecone.io/) for cloud indexes, or develop against Pinecone Local via the Python/REST APIs and your own app UI.

## Files

```
Pinecone/
├── docker-compose.yml   # Official pinecone-local service
├── start.sh             # Start stack
├── stop.sh              # Stop stack
├── test_connection.py   # API health check script
├── requirements.txt     # Python client for test script
└── README.md
```

## Troubleshooting

- **Port already in use**: change `PORT` and the port range in `docker-compose.yml`.
- **Slow on Apple Silicon**: expected with `linux/amd64` emulation; consider cloud dev for heavy workloads.
- **SDK errors**: ensure `pinecone` package is v6.x or later (`pip install -U "pinecone[grpc]"`).
- **Moving to production**: switch the client host to your Pinecone Cloud index and set a real `PINECONE_API_KEY`.
