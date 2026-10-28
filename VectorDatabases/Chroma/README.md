# ChromaDB (Vector Database)

Local ChromaDB server using the **official** Chroma Docker image (`chromadb/chroma`).

## What You Get


| Service      | URL                                            | Purpose                           |
| ------------ | ---------------------------------------------- | --------------------------------- |
| ChromaDB API | [http://localhost:8000](http://localhost:8000) | Official vector database HTTP API |


Data is persisted in `./chroma-data` on your machine (relative to this `Chroma/` directory).

## Official Docker Images


| Image                        | Registry                        |
| ---------------------------- | ------------------------------- |
| `chromadb/chroma`            | Docker Hub (used in this setup) |
| `ghcr.io/chroma-core/chroma` | GitHub Container Registry       |


Chroma does **not** ship an official admin/GUI Docker image. This stack runs only the official database server.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)
- `curl` (used by `start.sh` health check)



## Quick Start

```bash
cd Database/VectorDatabases/Chroma
chmod +x start.sh stop.sh
./start.sh
```

Stop the stack:

```bash
./stop.sh
```



## Access ChromaDB with Tuplex

Chroma does not publish an official GUI image. Use the unified **[Tuplex](../Tuplex/)** admin UI instead.

1. Start Chroma: `./start.sh`
2. Start Tuplex and connect to ChromaDB:

```bash
cd ../Tuplex
./start.sh
```

1. Open [http://127.0.0.1:8500](http://127.0.0.1:8500) → sign in → **Connect** → choose **ChromaDB** → host `localhost`, port `8000`.

See [Tuplex/README.md](../Tuplex/README.md) for MySQL and other backends.

## Verify API Access (CLI)

```bash
cd Database/VectorDatabases/Chroma
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_connection.py
```

Expected output includes a heartbeat response and a collections list (possibly empty on first run).

## Programmatic Access (Python)

```python
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
collection = client.get_or_create_collection("docs")

collection.add(
    ids=["1", "2"],
    documents=["Chroma is a vector database.", "Docker makes local setup easy."],
)

results = collection.query(query_texts=["vector database"], n_results=1)
print(results)
```



## Files

```
Chroma/
├── docker-compose.yml   # Official chromadb/chroma service only
├── start.sh             # Start stack
├── stop.sh              # Stop stack
├── test_connection.py   # API health check script
├── requirements.txt     # Python client for test script
├── chroma-data/         # Persisted DB files (created at runtime, gitignored)
└── README.md
```

Admin UI: [../Tuplex/README.md](../Tuplex/README.md)

## Troubleshooting

- **Port already in use**: change the host port in `docker-compose.yml` (for example `8001:8000`).
- **Container unhealthy**: run `docker compose logs chromadb` and confirm port `8000` is free.
- **Empty GUI**: create a collection first via Python/API, then refresh the UI.
- **GUI cannot reach server**: confirm Chroma is running and the URL is exactly `http://localhost:8000`.

