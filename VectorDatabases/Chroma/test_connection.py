#!/usr/bin/env python3
"""Quick check that ChromaDB is reachable on localhost:8000."""
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
heartbeat = client.heartbeat()
print("ChromaDB heartbeat:", heartbeat)

collections = client.list_collections()
print("Collections:", [c.name for c in collections])
