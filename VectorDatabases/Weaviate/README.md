# Weaviate (Vector Database)

Local Weaviate server using the **official** Weaviate Docker image (`cr.weaviate.io/semitechnologies/weaviate`).

## What You Get

| Service | URL | Purpose |
|---------|-----|---------|
| Weaviate REST API | http://localhost:8080 | Official vector database HTTP API |
| Weaviate gRPC | localhost:50051 | gRPC API for high-throughput clients |

Data is persisted in `./weaviate-data` on your machine (relative to this `Weaviate/` directory).

This stack runs Weaviate with `DEFAULT_VECTORIZER_MODULE: none`, so you bring your own vectors (same pattern as a minimal Chroma setup). Add modules later via `ENABLE_MODULES` in `docker-compose.yml` if you need built-in vectorization.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)
- `curl` (used by `start.sh` readiness check)

## Quick Start

```bash
cd Database/VectorDatabases/Weaviate
chmod +x start.sh stop.sh
./start.sh
```

Stop the stack:

```bash
./stop.sh
```

## Access Weaviate with a GUI

Weaviate ships a browser-based console (not a separate Docker GUI container):

1. Start Weaviate: `./start.sh`
2. Open **[Weaviate Console](https://console.weaviate.io/)**
3. Connect to your local instance:

```text
http://localhost:8080
```

4. Browse collections, run queries, and inspect schema from the UI.

## Verify API Access (CLI)

```bash
cd Database/VectorDatabases/Weaviate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_connection.py
```

Expected output includes `Weaviate ready: True` and a collections list (possibly empty on first run).

## Programmatic Access (Python)

```python
import weaviate
from weaviate.classes.config import Configure

with weaviate.connect_to_local() as client:
  articles = client.collections.create(
    name="Article",
    vector_config=Configure.Vectors.self_provided(),
  )

  articles = client.collections.get("Article")
  articles.data.insert(
    properties={"title": "Weaviate on Docker", "body": "Local vector search made easy."},
    vector=[0.1] * 1024,
  )

  response = articles.query.near_vector(near_vector=[0.1] * 1024, limit=1)
  print(response.objects[0].properties)
```

Use **1024** dimensions (or match your embedding model) when inserting self-provided vectors.

## Files

```
Weaviate/
├── docker-compose.yml   # Official Weaviate service
├── start.sh             # Start stack
├── stop.sh              # Stop stack
├── test_connection.py   # API health check script
├── requirements.txt     # Python client for test script
├── weaviate-data/       # Persisted DB files (created at runtime, gitignored)
└── README.md
```

## Troubleshooting

- **Port already in use**: change host ports in `docker-compose.yml` (for example `8081:8080`).
- **Container unhealthy**: run `docker compose logs weaviate` and confirm ports `8080` and `50051` are free.
- **Console cannot connect**: confirm Weaviate is running and the URL is exactly `http://localhost:8080`.
- **Data loss after stop**: always use `./stop.sh` (or `docker compose down`) so Weaviate can flush data to disk.
