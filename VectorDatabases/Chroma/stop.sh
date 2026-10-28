#!/bin/bash
# Stop ChromaDB stack

set -e
cd "$(dirname "$0")"

echo "Stopping ChromaDB stack..."
docker compose down

echo "Done."
