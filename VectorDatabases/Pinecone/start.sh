#!/bin/bash
# Start Pinecone Local via Docker Compose

set -e
cd "$(dirname "$0")"

echo "Starting Pinecone Local (ghcr.io/pinecone-io/pinecone-local)..."
docker compose up -d

echo ""
echo "Waiting for Pinecone Local to accept connections on port 5080..."
for _ in $(seq 1 60); do
  if nc -z localhost 5080 2>/dev/null; then
    break
  fi
  sleep 1
done

echo ""
echo "Pinecone Local API: http://localhost:5080"
echo "Index ports:        5080-5090"
echo ""
echo "Note: Pinecone Local is an in-memory emulator — data does not persist after stop."
echo "API keys are ignored; use any value (e.g. pclocal) in client code."
echo ""
echo "Or verify with: python test_connection.py"
echo "Stop with: ./stop.sh"
