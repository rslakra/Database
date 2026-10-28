#!/bin/bash
# Start official ChromaDB server via Docker Compose

set -e
cd "$(dirname "$0")"

echo "Starting ChromaDB (official chromadb/chroma image)..."
docker compose up -d

echo ""
echo "Waiting for ChromaDB to become healthy..."
for _ in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/v2/heartbeat >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo ""
echo "ChromaDB API:  http://localhost:8000"
echo ""
echo "Admin UI: cd ../Tuplex && ./start.sh  →  http://127.0.0.1:8500"
echo ""
echo "Or verify with: python test_connection.py"
echo "Stop with: ./stop.sh"
