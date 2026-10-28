#!/bin/bash
# Stop Pinecone Local stack

set -e
cd "$(dirname "$0")"

echo "Stopping Pinecone Local stack..."
docker compose down

echo "Done."
