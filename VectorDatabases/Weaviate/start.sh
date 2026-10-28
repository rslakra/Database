#!/bin/bash
# Start Weaviate server via Docker Compose

set -e
cd "$(dirname "$0")"

echo "Starting Weaviate (official semitechnologies/weaviate image)..."
docker compose up -d

echo ""
echo "Waiting for Weaviate to become ready..."
for _ in $(seq 1 60); do
  if curl -sf http://localhost:8080/v1/.well-known/ready >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo ""
echo "Weaviate API:  http://localhost:8080"
echo "Weaviate gRPC: localhost:50051"
echo ""
echo "GUI (official Weaviate Console, runs in your browser):"
echo "  https://console.weaviate.io/"
echo "  Connect to: http://localhost:8080"
echo ""
echo "Or verify with: python test_connection.py"
echo "Stop with: ./stop.sh"
