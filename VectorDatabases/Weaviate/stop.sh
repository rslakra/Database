#!/bin/bash
# Stop Weaviate stack

set -e
cd "$(dirname "$0")"

echo "Stopping Weaviate stack..."
docker compose down

echo "Done."
